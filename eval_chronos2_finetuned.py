import pandas as pd
import torch
from chronos.chronos2 import Chronos2Pipeline

df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])
df_us = df[df['marketplace'] == 'US'].copy()

cutoff = '2025-11-30'
pred_days = 60

# 准备测试数据
actual_totals, histories = {}, {}
for sku in df_us[df_us['date'] > cutoff]['sku'].unique()[:100]:
    sku_data = df_us[df_us['sku'] == sku].sort_values('date')
    hist = sku_data[sku_data['date'] <= cutoff]['sales_quantity'].values
    actual = sku_data[(sku_data['date'] > cutoff) & (sku_data['date'] <= '2026-01-29')]['sales_quantity'].sum()
    if len(hist) >= 60 and actual > 0:
        histories[sku] = hist
        actual_totals[sku] = actual

print(f"测试SKU数: {len(histories)}")

# 测试预训练模型
print("\n预训练模型:")
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
preds = {}
for sku, hist in histories.items():
    tensor = torch.tensor(hist, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    forecast = pipe.predict(tensor, prediction_length=pred_days)
    preds[sku] = max(0, forecast[0][0, 6, :].sum().item())

total_actual = sum(actual_totals.values())
total_error = sum(abs(actual_totals[s] - preds[s]) for s in histories)
print(f"准确率: {100 - total_error/total_actual*100:.1f}%")
del pipe; torch.cuda.empty_cache()

# 测试微调模型
print("\n微调模型:")
pipe = Chronos2Pipeline.from_pretrained("chronos2_finetuned_new/finetuned-ckpt", device_map="cuda", dtype=torch.float32)
preds = {}
for sku, hist in histories.items():
    tensor = torch.tensor(hist, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    forecast = pipe.predict(tensor, prediction_length=pred_days)
    preds[sku] = max(0, forecast[0][0, 6, :].sum().item())

total_error = sum(abs(actual_totals[s] - preds[s]) for s in histories)
print(f"准确率: {100 - total_error/total_actual*100:.1f}%")
