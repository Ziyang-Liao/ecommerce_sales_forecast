"""
在 SageMaker 上部署 Chronos-2 并运行预测
"""
import sys
sys.path.append("code_preprocess")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sagemaker import Session
from sagemaker.jumpstart.model import JumpStartModel
from preprocess import preprocess_data, PAST_COVARIATES, FUTURE_COVARIATES

# 配置
PREDICTION_LENGTH = 28
MARKETPLACE = "US"

print("=" * 60)
print("跨境电商销量预测 - Chronos-2 SageMaker 部署")
print("=" * 60)

# 1. 加载数据
print("\n[1/5] 加载数据...")
raw_df = pd.read_csv("data/sales_history.csv", parse_dates=["date", "launch_date"])
print(f"  总记录: {len(raw_df):,} 行")
print(f"  SKU数量: {raw_df['asin'].nunique()}")

# 筛选 US 站点活跃产品
us_df = raw_df[raw_df["marketplace"] == MARKETPLACE].copy()
latest_date = us_df["date"].max()
active_asins = us_df[us_df["date"] >= latest_date - timedelta(days=30)]["asin"].unique()
us_df = us_df[us_df["asin"].isin(active_asins)]
print(f"  US站点活跃SKU: {len(active_asins)}")

# 2. 预处理
print("\n[2/5] 数据预处理...")
df = preprocess_data(us_df, marketplace=MARKETPLACE)
print(f"  特征数量: {len(df.columns)}")

# 3. 部署端点
print("\n[3/5] 部署 Chronos-2 端点...")
session = Session()

js_model = JumpStartModel(
    model_id="pytorch-forecasting-chronos-2",
    instance_type="ml.g5.xlarge",
    role=None,
)
predictor = js_model.deploy()
print("  端点部署完成")

# 4. 构建请求并预测
print("\n[4/5] 执行预测...")

def build_payload(df, n_samples=50):
    """构建预测请求 (取前n个产品)"""
    inputs = []
    sample_asins = df["asin"].unique()[:n_samples]
    
    for asin in sample_asins:
        group = df[df["asin"] == asin].sort_values("date")
        
        entry = {
            "target": group["sales_quantity"].tolist(),
            "item_id": str(asin),
            "start": group["date"].iloc[0].isoformat(),
        }
        
        # 历史协变量
        valid_past = [c for c in PAST_COVARIATES if c in group.columns]
        entry["past_covariates"] = {
            col: group[col].fillna(0).tolist() for col in valid_past
        }
        
        # 未来协变量
        last_date = group["date"].max()
        future_dates = pd.date_range(last_date + timedelta(days=1), periods=PREDICTION_LENGTH)
        future_df = pd.DataFrame({"date": future_dates, "asin": asin, "sales_quantity": 0})
        future_df = preprocess_data(future_df, marketplace=MARKETPLACE)
        
        valid_future = [c for c in FUTURE_COVARIATES if c in future_df.columns]
        entry["future_covariates"] = {
            col: future_df[col].fillna(0).tolist() for col in valid_future
        }
        
        inputs.append(entry)
    
    return {
        "inputs": inputs,
        "parameters": {
            "prediction_length": PREDICTION_LENGTH,
            "freq": "D",
            "quantile_levels": [0.1, 0.5, 0.9]
        }
    }

payload = build_payload(df, n_samples=50)
print(f"  预测 {len(payload['inputs'])} 个产品")

response = predictor.predict(payload)
print("  预测完成")

# 5. 处理结果
print("\n[5/5] 处理预测结果...")

def response_to_df(response):
    dfs = []
    for pred in response["predictions"]:
        forecast_df = pd.DataFrame({
            "asin": pred.get("item_id"),
            "date": pd.date_range(pred["start"], periods=len(pred["mean"]), freq="D"),
            "forecast": pred["mean"],
            "lower_10": pred["0.1"],
            "upper_90": pred["0.9"],
        })
        dfs.append(forecast_df)
    return pd.concat(dfs, ignore_index=True)

forecast_df = response_to_df(response)
print(f"  预测结果: {len(forecast_df)} 行")

# 保存结果
output_file = f"forecast_{MARKETPLACE}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
forecast_df.to_csv(output_file, index=False)
print(f"  已保存: {output_file}")

# 展示部分结果
print("\n" + "=" * 60)
print("预测结果示例 (前3个产品)")
print("=" * 60)

for asin in forecast_df["asin"].unique()[:3]:
    hist = df[df["asin"] == asin].tail(14)
    pred = forecast_df[forecast_df["asin"] == asin]
    
    print(f"\n产品: {asin}")
    print(f"  历史14天平均销量: {hist['sales_quantity'].mean():.1f}")
    print(f"  预测28天平均销量: {pred['forecast'].mean():.1f}")
    print(f"  预测区间: [{pred['lower_10'].mean():.1f}, {pred['upper_90'].mean():.1f}]")

# 汇总统计
print("\n" + "=" * 60)
print("预测汇总")
print("=" * 60)
total_forecast = forecast_df.groupby("asin")["forecast"].sum()
print(f"  预测产品数: {len(total_forecast)}")
print(f"  预测天数: {PREDICTION_LENGTH}")
print(f"  预测总销量: {total_forecast.sum():,.0f}")
print(f"  平均每产品: {total_forecast.mean():,.0f}")

# 清理提示
print("\n" + "=" * 60)
print("注意: 端点正在运行中，会产生费用")
print("运行以下命令删除端点:")
print(f"  predictor.delete_predictor()")
print("=" * 60)
