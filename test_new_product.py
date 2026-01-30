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

# 新品：2025年8-10月上架，历史<60天
new_skus = df[(df['launch_date'] >= '2025-08-01') & (df['launch_date'] <= cutoff)]['sku'].unique()

# 产品特征（可以从同类产品学习）
product_cols = ['product_line', 'sale_price', 'original_price']
promo_cols = ['is_prime_day', 'is_black_friday_week', 'is_cyber_monday', 
              'is_christmas_season', 'is_halloween_season', 'is_major_sale_event']

# 产品线编码
product_line_map = {'led_strip': 1, 'smart_light': 2, 'tv_backlight': 3, 
                    'outdoor_light': 4, 'smart_sensor': 5, 'accessory': 6}

histories_sales = []  # 仅销量
histories_with_features = []  # 销量+产品特征+促销
actuals = []
sku_info = []

for sku in new_skus:
    sku_df = df[df['sku'] == sku].sort_values('date')
    train_df = sku_df[sku_df['date'] <= cutoff]
    test_df = sku_df[(sku_df['date'] >= pred_start) & (sku_df['date'] <= pred_end)]
    
    if len(train_df) < 10 or len(test_df) < 30:  # 新品历史可以很短
        continue
    
    sales = train_df['sales_quantity'].values.astype(np.float32)
    
    # 产品特征
    pl_code = product_line_map.get(train_df['product_line'].iloc[0], 0)
    price = train_df['sale_price'].fillna(0).values.astype(np.float32)
    price_norm = price / price.max() if price.max() > 0 else price
    
    # 促销特征
    promos = train_df[promo_cols].fillna(0).values.astype(np.float32)
    
    # 产品线作为常量特征
    pl_feature = np.full(len(sales), pl_code / 6, dtype=np.float32)
    
    histories_sales.append(sales)
    histories_with_features.append(np.vstack([sales, pl_feature, price_norm, promos.T]))
    actuals.append(test_df['sales_quantity'].sum())
    sku_info.append({
        'sku': sku, 
        'product_line': train_df['product_line'].iloc[0],
        'history_days': len(train_df),
        'actual': test_df['sales_quantity'].sum()
    })

print(f"新品数量: {len(histories_sales)}")
print(f"特征维度: 1(sales) + 1(product_line) + 1(price) + {len(promo_cols)}(promo) = {1+1+1+len(promo_cols)}")

def evaluate(pipe, histories, actuals, pred_days):
    preds = []
    for h, actual in zip(histories, actuals):
        if isinstance(h, np.ndarray) and h.ndim == 2:
            tensor = torch.tensor(h, dtype=torch.float32).unsqueeze(0)
        else:
            tensor = torch.tensor(h, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        pred = pipe.predict(tensor, prediction_length=pred_days)[0][0, 6, :].sum().item()
        preds.append(pred)
    
    total_actual = sum(actuals)
    total_error = sum(abs(a - p) for a, p in zip(actuals, preds))
    return 100 - (total_error / total_actual * 100), preds

pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)

print("\n=== 新品预测对比 ===")
acc_sales, preds_sales = evaluate(pipe, histories_sales, actuals, pred_days)
print(f"仅销量:           {acc_sales:.1f}%")

acc_features, preds_features = evaluate(pipe, histories_with_features, actuals, pred_days)
print(f"销量+产品+促销:   {acc_features:.1f}%")

print(f"\n差异: {acc_features - acc_sales:+.1f}%")

# 按产品线分析
print("\n=== 按产品线分析 ===")
for pl in product_line_map.keys():
    pl_idx = [i for i, info in enumerate(sku_info) if info['product_line'] == pl]
    if len(pl_idx) < 2:
        continue
    pl_actual = sum(actuals[i] for i in pl_idx)
    pl_err_sales = sum(abs(actuals[i] - preds_sales[i]) for i in pl_idx)
    pl_err_feat = sum(abs(actuals[i] - preds_features[i]) for i in pl_idx)
    print(f"{pl:15} ({len(pl_idx):2}个): 仅销量 {100-pl_err_sales/pl_actual*100:.1f}% | +特征 {100-pl_err_feat/pl_actual*100:.1f}%")
