"""Chronos 微调 - 官方方式"""
import pandas as pd
import numpy as np
import torch
from pathlib import Path
from gluonts.dataset.arrow import ArrowWriter

print("=" * 60)
print("Chronos 微调 - 电商销量数据")
print("=" * 60)

# 1. 准备Arrow格式数据
print("\n[1/3] 准备训练数据...")
raw_df = pd.read_csv("data/sales_history.csv", parse_dates=["date", "launch_date"])
us_df = raw_df[raw_df["marketplace"] == "US"].copy()

train_data = []
for asin, group in us_df.groupby("asin"):
    group = group.sort_values("date")
    if len(group) >= 60:
        train_data.append({
            "start": pd.Timestamp(group["date"].iloc[0]),
            "target": group["sales_quantity"].values.astype(np.float32),
        })

print(f"  训练序列数: {len(train_data)}")

Path("train_data").mkdir(exist_ok=True)
ArrowWriter(compression="lz4").write_to_file(train_data, path="train_data/data.arrow")
print("  数据已保存到 train_data/data.arrow")

# 2. 创建配置文件
print("\n[2/3] 创建微调配置...")
config = """
model_id: amazon/chronos-t5-small
output_dir: ./chronos_finetuned
training_data_paths:
  - train_data/data.arrow
probability:
  - 1.0
context_length: 256
prediction_length: 64
min_past: 60
max_steps: 1000
save_steps: 500
log_steps: 100
per_device_train_batch_size: 16
learning_rate: 1e-4
optim: adamw_torch
shuffle_buffer_length: 10000
gradient_accumulation_steps: 1
model_dtype: bfloat16
tf32: true
torch_compile: false
num_samples: 20
temperature: 1.0
top_k: 50
top_p: 1.0
"""

with open("finetune_config.yaml", "w") as f:
    f.write(config)
print("  配置已保存")

# 3. 运行微调
print("\n[3/3] 开始微调...")
import subprocess
result = subprocess.run(
    ["python3", "-m", "chronos.scripts.training", "--config", "finetune_config.yaml"],
    capture_output=False
)
