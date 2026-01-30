"""评估微调模型 vs 原始模型"""
import pandas as pd
import numpy as np
import torch
from datetime import timedelta
from chronos import ChronosPipeline

raw_df = pd.read_csv("data/sales_history.csv", parse_dates=["date", "launch_date"])
us_df = raw_df[raw_df["marketplace"] == "US"].copy()

latest_date = us_df["date"].max()
cutoff_date = latest_date - timedelta(days=28)

train_df = us_df[us_df["date"] <= cutoff_date]
test_df = us_df[us_df["date"] > cutoff_date]

test_asins = test_df.groupby("asin").size()
valid_asins = test_asins[test_asins >= 28].index[:50]

print("=" * 60)
print("微调模型 vs 原始模型 对比")
print("=" * 60)

models = [
    ("amazon/chronos-t5-small", "原始 T5-Small"),
    ("./chronos_finetuned/run-0/checkpoint-500", "微调模型"),
]

results = {}

for model_path, name in models:
    print(f"\n评估 {name}...")
    
    pipeline = ChronosPipeline.from_pretrained(model_path, device_map="cuda", torch_dtype=torch.float16)
    
    all_actual, all_pred = [], []
    
    for asin in valid_asins:
        hist = train_df[train_df["asin"] == asin].sort_values("date")
        if len(hist) < 30:
            continue
            
        context = torch.tensor(hist["sales_quantity"].values, dtype=torch.float32)
        forecast = pipeline.predict(context, 28, num_samples=20)
        pred = np.median(forecast[0].numpy(), axis=0)
        
        actual = test_df[test_df["asin"] == asin].sort_values("date")["sales_quantity"].values[:28]
        
        if len(actual) == 28:
            all_actual.extend(actual)
            all_pred.extend(pred)
    
    actual = np.array(all_actual)
    pred = np.array(all_pred)
    
    mae = np.mean(np.abs(actual - pred))
    rmse = np.sqrt(np.mean((actual - pred) ** 2))
    wape = np.sum(np.abs(actual - pred)) / np.sum(np.abs(actual)) * 100
    bias = np.mean(pred - actual)
    
    results[name] = {"MAE": mae, "RMSE": rmse, "WAPE": wape, "Bias": bias}

print("\n" + "=" * 60)
print("评估结果")
print("=" * 60)
print(f"{'模型':<20} {'MAE':>8} {'RMSE':>8} {'WAPE%':>8} {'Bias':>8}")
print("-" * 60)

for name, m in results.items():
    print(f"{name:<20} {m['MAE']:>8.2f} {m['RMSE']:>8.2f} {m['WAPE']:>8.1f} {m['Bias']:>+8.2f}")

# 改进幅度
if len(results) == 2:
    orig = results["原始 T5-Small"]
    fine = results["微调模型"]
    print(f"\n改进: WAPE {orig['WAPE']:.1f}% -> {fine['WAPE']:.1f}% ({(fine['WAPE']-orig['WAPE'])/orig['WAPE']*100:+.1f}%)")
