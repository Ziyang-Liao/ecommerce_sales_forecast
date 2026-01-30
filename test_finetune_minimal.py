import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('data/sales_history_enriched.csv', parse_dates=['date', 'launch_date'])
df = df[df['marketplace'] == 'US'].sort_values(['sku', 'date'])

# 只保留促销日字段
promo_cols = ['is_prime_day', 'is_black_friday_week', 'is_cyber_monday', 
              'is_christmas_season', 'is_halloween_season', 'is_major_sale_event']

test_skus = df['sku'].unique()[:100]
cutoff = pd.Timestamp('2025-10-31')
pred_start = pd.Timestamp('2025-11-01')
pred_end = pd.Timestamp('2025-12-31')
pred_days = 61

histories = []
actuals = []

for sku in test_skus:
    sku_df = df[df['sku'] == sku].sort_values('date')
    train_df = sku_df[sku_df['date'] <= cutoff]
    test_df = sku_df[(sku_df['date'] >= pred_start) & (sku_df['date'] <= pred_end)]
    
    if len(train_df) < 60 or len(test_df) < 30:
        continue
    
    sales = train_df['sales_quantity'].values.astype(np.float32)
    covs = train_df[promo_cols].fillna(0).values.astype(np.float32)
    histories.append(np.vstack([sales, covs.T]))
    actuals.append(test_df['sales_quantity'].sum())

print(f"有效SKU: {len(histories)}, 协变量: sales + {len(promo_cols)}个促销字段")

def evaluate(pipe, histories, actuals):
    total_actual = total_error = 0
    for h, actual in zip(histories, actuals):
        tensor = torch.tensor(h, dtype=torch.float32).unsqueeze(0)
        pred = pipe.predict(tensor, prediction_length=pred_days)[0][0, 6, :].sum().item()
        total_actual += actual
        total_error += abs(actual - pred)
    return 100 - (total_error / total_actual * 100)

# 1. 预训练
print("\n=== 预训练模型 + 促销字段 ===")
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
acc_pre = evaluate(pipe, histories, actuals)
print(f"准确率: {acc_pre:.1f}%")

# 2. 微调
print("\n=== 微调中... ===")
train_tensors = [torch.tensor(h, dtype=torch.float32) for h in histories]
pipe_ft = pipe.fit(
    inputs=train_tensors,
    prediction_length=pred_days,
    num_steps=300,
    learning_rate=1e-6,
    batch_size=8,
    finetune_mode='full',
    output_dir='./ft_promo',
)

# 3. 微调后
print("\n=== 微调模型 + 促销字段 ===")
acc_ft = evaluate(pipe_ft, histories, actuals)
print(f"准确率: {acc_ft:.1f}%")

print("\n" + "="*50)
print("结果对比 (sales + 6个促销字段)")
print("="*50)
print(f"预训练: {acc_pre:.1f}%")
print(f"微调后: {acc_ft:.1f}%")
print(f"差异:   {acc_ft - acc_pre:+.1f}%")
