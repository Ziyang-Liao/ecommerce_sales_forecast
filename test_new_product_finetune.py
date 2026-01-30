import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('data/sales_history_enriched.csv', parse_dates=['date', 'launch_date'])
df = df[df['marketplace'] == 'US'].sort_values(['sku', 'date'])

cutoff = pd.Timestamp('2025-10-31')
pred_start = pd.Timestamp('2025-11-01')
pred_end = pd.Timestamp('2025-12-31')
pred_days = 61

# 新品
new_skus = df[(df['launch_date'] >= '2025-08-01') & (df['launch_date'] <= cutoff)]['sku'].unique()
# 老品（用于微调）
old_skus = df[df['launch_date'] < '2025-08-01']['sku'].unique()[:100]

product_line_map = {'led_strip': 1, 'smart_light': 2, 'tv_backlight': 3, 
                    'outdoor_light': 4, 'smart_sensor': 5, 'accessory': 6}
promo_cols = ['is_prime_day', 'is_black_friday_week', 'is_cyber_monday', 
              'is_christmas_season', 'is_halloween_season', 'is_major_sale_event']

def prepare_features(sku_df):
    sales = sku_df['sales_quantity'].values.astype(np.float32)
    pl_code = product_line_map.get(sku_df['product_line'].iloc[0], 0)
    price = sku_df['sale_price'].fillna(0).values.astype(np.float32)
    price_norm = price / price.max() if price.max() > 0 else price
    promos = sku_df[promo_cols].fillna(0).values.astype(np.float32)
    pl_feature = np.full(len(sales), pl_code / 6, dtype=np.float32)
    return np.vstack([sales, pl_feature, price_norm, promos.T])

# 准备老品数据用于微调
train_data = []
for sku in old_skus:
    sku_df = df[df['sku'] == sku].sort_values('date')
    train_df = sku_df[sku_df['date'] <= cutoff]
    if len(train_df) >= 60:
        train_data.append(torch.tensor(prepare_features(train_df), dtype=torch.float32))

# 准备新品测试数据
test_histories = []
test_actuals = []
for sku in new_skus:
    sku_df = df[df['sku'] == sku].sort_values('date')
    train_df = sku_df[sku_df['date'] <= cutoff]
    test_df = sku_df[(sku_df['date'] >= pred_start) & (sku_df['date'] <= pred_end)]
    if len(train_df) >= 10 and len(test_df) >= 30:
        test_histories.append(prepare_features(train_df))
        test_actuals.append(test_df['sales_quantity'].sum())

print(f"微调数据: {len(train_data)}个老品")
print(f"测试数据: {len(test_histories)}个新品")

def evaluate(pipe, histories, actuals):
    total_actual = total_error = 0
    for h, actual in zip(histories, actuals):
        tensor = torch.tensor(h, dtype=torch.float32).unsqueeze(0)
        pred = pipe.predict(tensor, prediction_length=pred_days)[0][0, 6, :].sum().item()
        total_actual += actual
        total_error += abs(actual - pred)
    return 100 - (total_error / total_actual * 100)

# 1. 预训练
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
acc_pre = evaluate(pipe, test_histories, test_actuals)
print(f"\n预训练 + 产品特征: {acc_pre:.1f}%")

# 2. 微调
print("\n微调中...")
pipe_ft = pipe.fit(
    inputs=train_data,
    prediction_length=pred_days,
    num_steps=300,
    learning_rate=1e-6,
    batch_size=8,
    finetune_mode='full',
    output_dir='./ft_new_product',
)

acc_ft = evaluate(pipe_ft, test_histories, test_actuals)
print(f"微调后 + 产品特征: {acc_ft:.1f}%")

print("\n" + "="*50)
print("新品预测结果 (销量+产品线+价格+促销)")
print("="*50)
print(f"预训练: {acc_pre:.1f}%")
print(f"微调后: {acc_ft:.1f}%")
print(f"差异:   {acc_ft - acc_pre:+.1f}%")
