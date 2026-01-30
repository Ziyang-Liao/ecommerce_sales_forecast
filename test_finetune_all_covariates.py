import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('data/sales_history_enriched.csv', parse_dates=['date', 'launch_date'])
df = df[df['marketplace'] == 'US'].sort_values(['sku', 'date'])

covariate_cols = [
    'discount_rate', 'ad_spend', 'fba_inventory', 'is_lightning_deal', 
    'is_coupon_active', 'is_deal_of_day', 'bsr_rank', 'rating', 'review_count',
    'is_prime_day', 'is_black_friday_week', 'is_cyber_monday', 'is_christmas_season',
    'is_halloween_season', 'is_back_to_school', 'is_major_sale_event',
    'days_since_launch', 'lifecycle_stage_code'
]

test_skus = df['sku'].unique()[:100]
cutoff = pd.Timestamp('2025-10-31')
pred_start = pd.Timestamp('2025-11-01')
pred_end = pd.Timestamp('2025-12-31')
pred_days = 61

# 准备数据
histories_cov = []  # 带协变量
histories_sales = []  # 仅销量
actuals = []

for sku in test_skus:
    sku_df = df[df['sku'] == sku].sort_values('date')
    train_df = sku_df[sku_df['date'] <= cutoff]
    test_df = sku_df[(sku_df['date'] >= pred_start) & (sku_df['date'] <= pred_end)]
    
    if len(train_df) < 60 or len(test_df) < 30:
        continue
    
    sales = train_df['sales_quantity'].values.astype(np.float32)
    covs = train_df[covariate_cols].fillna(0).values.astype(np.float32)
    
    histories_cov.append(np.vstack([sales, covs.T]))
    histories_sales.append(torch.tensor(sales))
    actuals.append(test_df['sales_quantity'].sum())

print(f"有效SKU数: {len(histories_cov)}")

def evaluate(pipe, histories, actuals):
    total_actual = total_error = 0
    for h, actual in zip(histories, actuals):
        if isinstance(h, np.ndarray):
            tensor = torch.tensor(h, dtype=torch.float32).unsqueeze(0)
        else:
            tensor = h.unsqueeze(0).unsqueeze(0)
        forecast = pipe.predict(tensor, prediction_length=pred_days)
        pred = forecast[0][0, 6, :].sum().item()
        total_actual += actual
        total_error += abs(actual - pred)
    return 100 - (total_error / total_actual * 100)

# 1. 预训练 + 全部协变量
print("\n=== 预训练模型 + 全部协变量 ===")
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
acc_pretrained_cov = evaluate(pipe, histories_cov, actuals)
print(f"准确率: {acc_pretrained_cov:.1f}%")

# 2. 微调 (用带协变量的数据)
print("\n=== 微调中 (全部协变量数据) ===")
train_tensors = [torch.tensor(h, dtype=torch.float32) for h in histories_cov]
pipe_ft = pipe.fit(
    inputs=train_tensors,
    prediction_length=pred_days,
    num_steps=300,
    learning_rate=1e-6,
    batch_size=8,
    finetune_mode='full',
    output_dir='./ft_all_cov',
)
print("微调完成")

# 3. 微调模型 + 全部协变量
print("\n=== 微调模型 + 全部协变量 ===")
acc_finetuned_cov = evaluate(pipe_ft, histories_cov, actuals)
print(f"准确率: {acc_finetuned_cov:.1f}%")

print("\n" + "="*50)
print("结果对比 (预测2025年11-12月, 全部协变量)")
print("="*50)
print(f"预训练 + 全部协变量: {acc_pretrained_cov:.1f}%")
print(f"微调后 + 全部协变量: {acc_finetuned_cov:.1f}%")
print(f"差异: {acc_finetuned_cov - acc_pretrained_cov:+.1f}%")
