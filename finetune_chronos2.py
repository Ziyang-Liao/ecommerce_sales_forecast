import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline

# 加载数据
df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])
df_us = df[df['marketplace'] == 'US'].copy()

# 准备训练数据 (截止到2025-11-30)
cutoff = '2025-11-30'
train_data = []
for sku in df_us['sku'].unique():
    sku_data = df_us[df_us['sku'] == sku].sort_values('date')
    hist = sku_data[sku_data['date'] <= cutoff]['sales_quantity'].values.astype(np.float32)
    if len(hist) >= 60:
        train_data.append(torch.tensor(hist))

print(f"训练SKU数: {len(train_data)}")

# 加载模型
print("加载模型...")
pipe = Chronos2Pipeline.from_pretrained(
    "autogluon/chronos-2-small",
    device_map="cuda",
    dtype=torch.float32
)

# 微调
print("开始微调...")
finetuned = pipe.fit(
    inputs=train_data,
    prediction_length=60,
    num_steps=500,
    learning_rate=1e-6,
    batch_size=32,
    output_dir="chronos2_finetuned_new",
)

print("微调完成!")
