"""
跨境电商销量预测 - Chronos-2 本地推理演示
"""
import sys
sys.path.append("code_preprocess")

import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta
from chronos import ChronosPipeline

# 配置
PREDICTION_LENGTH = 28
MARKETPLACE = "US"
N_SAMPLES = 20  # 演示用，取20个产品

print("=" * 60)
print("跨境电商销量预测 - Chronos-2 推理演示")
print("=" * 60)

# 1. 加载数据
print("\n[1/4] 加载数据...")
raw_df = pd.read_csv("data/sales_history.csv", parse_dates=["date", "launch_date"])
print(f"  总记录: {len(raw_df):,} 行")

# 筛选 US 站点活跃产品
us_df = raw_df[raw_df["marketplace"] == MARKETPLACE].copy()
latest_date = us_df["date"].max()
active_asins = us_df[us_df["date"] >= latest_date - timedelta(days=30)]["asin"].unique()
us_df = us_df[us_df["asin"].isin(active_asins)]
print(f"  US站点活跃SKU: {len(active_asins)}")

# 2. 加载模型
print("\n[2/4] 加载 Chronos 模型...")
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",  # 使用小模型演示
    device_map="cpu",
    torch_dtype=torch.float32,
)
print("  模型加载完成")

# 3. 执行预测
print(f"\n[3/4] 预测 {N_SAMPLES} 个产品...")

results = []
sample_asins = us_df["asin"].unique()[:N_SAMPLES]

for i, asin in enumerate(sample_asins):
    group = us_df[us_df["asin"] == asin].sort_values("date")
    context = torch.tensor(group["sales_quantity"].values, dtype=torch.float32)
    
    # 预测
    forecast = pipeline.predict(context, PREDICTION_LENGTH, num_samples=20)
    
    # 计算分位数
    low, median, high = np.quantile(forecast[0].numpy(), [0.1, 0.5, 0.9], axis=0)
    
    # 生成日期
    last_date = group["date"].max()
    future_dates = pd.date_range(last_date + timedelta(days=1), periods=PREDICTION_LENGTH)
    
    for j, date in enumerate(future_dates):
        results.append({
            "asin": asin,
            "date": date,
            "forecast": median[j],
            "lower_10": low[j],
            "upper_90": high[j],
        })
    
    if (i + 1) % 5 == 0:
        print(f"  已完成 {i + 1}/{N_SAMPLES}")

forecast_df = pd.DataFrame(results)
print(f"  预测完成: {len(forecast_df)} 行")

# 4. 展示结果
print("\n[4/4] 预测结果")
print("=" * 60)

for asin in sample_asins[:5]:
    hist = us_df[us_df["asin"] == asin].tail(14)
    pred = forecast_df[forecast_df["asin"] == asin]
    product_line = us_df[us_df["asin"] == asin]["product_line"].iloc[0]
    
    hist_avg = hist["sales_quantity"].mean()
    pred_avg = pred["forecast"].mean()
    change = (pred_avg - hist_avg) / hist_avg * 100 if hist_avg > 0 else 0
    
    print(f"\n产品: {asin} ({product_line})")
    print(f"  历史14天均值: {hist_avg:.1f}")
    print(f"  预测28天均值: {pred_avg:.1f} ({change:+.1f}%)")
    print(f"  预测区间: [{pred['lower_10'].mean():.1f}, {pred['upper_90'].mean():.1f}]")

# 汇总
print("\n" + "=" * 60)
print("预测汇总")
print("=" * 60)

total_hist = us_df[us_df["asin"].isin(sample_asins)].groupby("asin").tail(28)["sales_quantity"].sum()
total_pred = forecast_df["forecast"].sum()

print(f"  预测产品数: {N_SAMPLES}")
print(f"  预测天数: {PREDICTION_LENGTH}")
print(f"  历史28天总销量: {total_hist:,.0f}")
print(f"  预测28天总销量: {total_pred:,.0f}")
print(f"  变化: {(total_pred - total_hist) / total_hist * 100:+.1f}%")

# 保存
output_file = f"forecast_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
forecast_df.to_csv(output_file, index=False)
print(f"\n预测结果已保存: {output_file}")
