"""
跨境电商销量预测 - 完整预测与评估
"""
import sys
sys.path.append("code_preprocess")
sys.path.append("code_evaluate")

import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta
from chronos import ChronosPipeline
from evaluate import calc_metrics

PREDICTION_LENGTH = 28
MARKETPLACE = "US"
N_SAMPLES = 50

print("=" * 70)
print("跨境电商销量预测 - Chronos 模型效果评估")
print("=" * 70)

# 加载数据
print("\n[1/5] 加载数据...")
raw_df = pd.read_csv("data/sales_history.csv", parse_dates=["date", "launch_date"])

us_df = raw_df[raw_df["marketplace"] == MARKETPLACE].copy()
latest_date = us_df["date"].max()

# 划分训练集和测试集 (最后28天作为测试)
cutoff_date = latest_date - timedelta(days=PREDICTION_LENGTH)
train_df = us_df[us_df["date"] <= cutoff_date]
test_df = us_df[(us_df["date"] > cutoff_date) & (us_df["date"] <= latest_date)]

# 选择有完整测试数据的产品
valid_asins = test_df.groupby("asin").size()
valid_asins = valid_asins[valid_asins >= PREDICTION_LENGTH - 2].index.tolist()
sample_asins = valid_asins[:N_SAMPLES]

print(f"  训练数据截止: {cutoff_date.date()}")
print(f"  测试数据: {cutoff_date.date()} ~ {latest_date.date()}")
print(f"  评估产品数: {len(sample_asins)}")

# 加载模型
print("\n[2/5] 加载 Chronos 模型...")
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",
    torch_dtype=torch.float32,
)
print("  模型加载完成")

# 预测
print(f"\n[3/5] 执行预测...")
results = []

for i, asin in enumerate(sample_asins):
    train_group = train_df[train_df["asin"] == asin].sort_values("date")
    if len(train_group) < 30:
        continue
    
    context = torch.tensor(train_group["sales_quantity"].values, dtype=torch.float32)
    forecast = pipeline.predict(context, PREDICTION_LENGTH, num_samples=20)
    
    low, median, high = np.quantile(forecast[0].numpy(), [0.1, 0.5, 0.9], axis=0)
    
    last_date = train_group["date"].max()
    future_dates = pd.date_range(last_date + timedelta(days=1), periods=PREDICTION_LENGTH)
    
    for j, date in enumerate(future_dates):
        results.append({
            "asin": asin,
            "date": date,
            "forecast": median[j],
            "lower_10": low[j],
            "upper_90": high[j],
        })
    
    if (i + 1) % 10 == 0:
        print(f"  已完成 {i + 1}/{len(sample_asins)}")

forecast_df = pd.DataFrame(results)
print(f"  预测完成: {len(forecast_df)} 行")

# 评估
print("\n[4/5] 模型评估...")

# 合并预测和实际值
eval_df = forecast_df.merge(
    test_df[["asin", "date", "sales_quantity"]],
    on=["asin", "date"],
    how="inner"
)

if len(eval_df) > 0:
    # 整体指标
    overall_metrics = calc_metrics(eval_df["sales_quantity"], eval_df["forecast"])
    
    print("\n整体评估指标:")
    print(f"  MAE:  {overall_metrics['MAE']:.2f}")
    print(f"  RMSE: {overall_metrics['RMSE']:.2f}")
    print(f"  MAPE: {overall_metrics['MAPE']:.2f}%")
    print(f"  WAPE: {overall_metrics['WAPE']:.2f}%")
    print(f"  Bias: {overall_metrics['Bias']:.2f}")
    
    # 按产品评估
    print("\n按产品评估 (Top 10):")
    product_metrics = []
    for asin in eval_df["asin"].unique():
        prod_df = eval_df[eval_df["asin"] == asin]
        if len(prod_df) >= 5:
            m = calc_metrics(prod_df["sales_quantity"], prod_df["forecast"])
            m["asin"] = asin
            m["n_days"] = len(prod_df)
            product_metrics.append(m)
    
    metrics_df = pd.DataFrame(product_metrics).sort_values("WAPE")
    print(metrics_df.head(10).to_string(index=False))
    
    # 按产品线评估
    print("\n按产品线评估:")
    eval_df = eval_df.merge(
        us_df[["asin", "product_line"]].drop_duplicates(),
        on="asin",
        how="left"
    )
    
    for pl in eval_df["product_line"].unique():
        pl_df = eval_df[eval_df["product_line"] == pl]
        if len(pl_df) > 0:
            m = calc_metrics(pl_df["sales_quantity"], pl_df["forecast"])
            print(f"  {pl:15s}: WAPE={m['WAPE']:.1f}%, MAE={m['MAE']:.1f}")

# 结果展示
print("\n[5/5] 预测示例")
print("=" * 70)

for asin in sample_asins[:3]:
    train_hist = train_df[train_df["asin"] == asin].tail(14)
    test_actual = test_df[test_df["asin"] == asin]
    pred = forecast_df[forecast_df["asin"] == asin]
    product_line = us_df[us_df["asin"] == asin]["product_line"].iloc[0]
    
    print(f"\n产品: {asin} ({product_line})")
    print(f"  训练期末14天均值: {train_hist['sales_quantity'].mean():.1f}")
    print(f"  测试期实际均值:   {test_actual['sales_quantity'].mean():.1f}")
    print(f"  预测均值:         {pred['forecast'].mean():.1f}")
    print(f"  预测区间:         [{pred['lower_10'].mean():.1f}, {pred['upper_90'].mean():.1f}]")

# 保存
output_file = f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
if len(eval_df) > 0:
    eval_df.to_csv(output_file, index=False)
    print(f"\n评估结果已保存: {output_file}")

print("\n" + "=" * 70)
print("评估完成")
print("=" * 70)
