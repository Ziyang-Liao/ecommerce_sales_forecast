import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline

# 加载数据
df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])
df_us = df[df['marketplace'] == 'US'].copy()

cutoff = '2025-11-30'

# 只用历史超过1年的SKU
train_data = []
for sku in df_us['sku'].unique():
    sku_data = df_us[df_us['sku'] == sku].sort_values('date')
    hist = sku_data[sku_data['date'] <= cutoff]['sales_quantity'].values.astype(np.float32)
    if len(hist) >= 365:  # 至少1年历史
        train_data.append(torch.tensor(hist))

print(f"训练SKU数: {len(train_data)}")

# 准备测试数据
actual_totals, histories = {}, {}
for sku in df_us[df_us['date'] > cutoff]['sku'].unique()[:100]:
    sku_data = df_us[df_us['sku'] == sku].sort_values('date')
    hist = sku_data[sku_data['date'] <= cutoff]['sales_quantity'].values
    actual = sku_data[(sku_data['date'] > cutoff) & (sku_data['date'] <= '2026-01-29')]['sales_quantity'].sum()
    if len(hist) >= 60 and actual > 0:
        histories[sku] = hist
        actual_totals[sku] = actual

total_actual = sum(actual_totals.values())

# 测试不同超参
configs = [
    {"lr": 1e-7, "steps": 200, "batch": 64},
    {"lr": 5e-7, "steps": 300, "batch": 64},
    {"lr": 1e-6, "steps": 200, "batch": 128},
]

for cfg in configs:
    print(f"\n=== lr={cfg['lr']}, steps={cfg['steps']}, batch={cfg['batch']} ===")
    
    pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
    
    finetuned = pipe.fit(
        inputs=train_data,
        prediction_length=60,
        num_steps=cfg['steps'],
        learning_rate=cfg['lr'],
        batch_size=cfg['batch'],
        output_dir=f"ft_test_{cfg['lr']}",
    )
    
    # 评估
    preds = {}
    for sku, hist in histories.items():
        tensor = torch.tensor(hist, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        forecast = finetuned.predict(tensor, prediction_length=60)
        preds[sku] = max(0, forecast[0][0, 6, :].sum().item())
    
    total_error = sum(abs(actual_totals[s] - preds[s]) for s in histories)
    acc = 100 - total_error/total_actual*100
    print(f"准确率: {acc:.1f}%")
    
    del pipe, finetuned
    torch.cuda.empty_cache()

print("\n基准 (预训练): 92.2%")
