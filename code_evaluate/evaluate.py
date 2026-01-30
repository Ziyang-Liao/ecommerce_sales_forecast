"""
Govee 销量预测 - 评估指标模块
"""
import pandas as pd
import numpy as np
from typing import Dict


def calc_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """计算预测评估指标"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    
    # MAE - 平均绝对误差
    mae = np.mean(np.abs(y_true - y_pred))
    
    # RMSE - 均方根误差
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    # MAPE - 平均绝对百分比误差 (避免除零)
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    
    # WAPE - 加权绝对百分比误差 (更适合销量预测)
    wape = np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100
    
    # Bias - 偏差 (正=高估, 负=低估)
    bias = np.mean(y_pred - y_true)
    
    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
        "WAPE": round(wape, 2),
        "Bias": round(bias, 2),
    }


def calc_quantile_loss(y_true: np.ndarray, y_pred: np.ndarray, q: float) -> float:
    """计算分位数损失"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    errors = y_true - y_pred
    loss = np.mean(np.maximum(q * errors, (q - 1) * errors))
    return round(loss, 4)


def evaluate_forecast(actual_df: pd.DataFrame, forecast_df: pd.DataFrame,
                      id_col: str = "asin", date_col: str = "date",
                      actual_col: str = "sales_quantity", 
                      forecast_col: str = "forecast") -> pd.DataFrame:
    """
    评估预测结果
    
    Args:
        actual_df: 实际销量 DataFrame
        forecast_df: 预测结果 DataFrame
    
    Returns:
        按产品汇总的评估指标
    """
    # 合并实际值和预测值
    merged = forecast_df.merge(
        actual_df[[id_col, date_col, actual_col]],
        on=[id_col, date_col],
        how="inner"
    )
    
    if len(merged) == 0:
        raise ValueError("无匹配数据，请检查日期范围")
    
    # 按产品计算指标
    results = []
    for item_id, group in merged.groupby(id_col):
        metrics = calc_metrics(group[actual_col], group[forecast_col])
        metrics[id_col] = item_id
        metrics["n_days"] = len(group)
        
        # 分位数损失
        if "lower_10" in group.columns:
            metrics["QL_10"] = calc_quantile_loss(group[actual_col], group["lower_10"], 0.1)
        if "upper_90" in group.columns:
            metrics["QL_90"] = calc_quantile_loss(group[actual_col], group["upper_90"], 0.9)
        
        results.append(metrics)
    
    result_df = pd.DataFrame(results)
    cols = [id_col, "n_days", "MAE", "RMSE", "MAPE", "WAPE", "Bias"]
    cols += [c for c in ["QL_10", "QL_90"] if c in result_df.columns]
    
    return result_df[cols]


def evaluate_by_period(actual_df: pd.DataFrame, forecast_df: pd.DataFrame,
                       id_col: str = "asin", date_col: str = "date",
                       actual_col: str = "sales_quantity",
                       forecast_col: str = "forecast") -> pd.DataFrame:
    """按时间段评估 (旺季 vs 淡季)"""
    merged = forecast_df.merge(
        actual_df[[id_col, date_col, actual_col]],
        on=[id_col, date_col],
        how="inner"
    )
    
    # 划分旺季/淡季
    merged["period"] = merged[date_col].dt.month.map(
        lambda m: "peak" if m in [10, 11, 12] else "normal"
    )
    
    results = []
    for period, group in merged.groupby("period"):
        metrics = calc_metrics(group[actual_col], group[forecast_col])
        metrics["period"] = period
        metrics["n_records"] = len(group)
        results.append(metrics)
    
    return pd.DataFrame(results)[["period", "n_records", "MAE", "RMSE", "MAPE", "WAPE"]]


def print_summary(metrics_df: pd.DataFrame):
    """打印评估摘要"""
    print("=" * 50)
    print("预测评估摘要")
    print("=" * 50)
    print(f"产品数量: {len(metrics_df)}")
    print(f"平均 MAE:  {metrics_df['MAE'].mean():.2f}")
    print(f"平均 RMSE: {metrics_df['RMSE'].mean():.2f}")
    print(f"平均 MAPE: {metrics_df['MAPE'].mean():.2f}%")
    print(f"平均 WAPE: {metrics_df['WAPE'].mean():.2f}%")
    print("=" * 50)
    
    # 最佳/最差产品
    best = metrics_df.loc[metrics_df["WAPE"].idxmin()]
    worst = metrics_df.loc[metrics_df["WAPE"].idxmax()]
    print(f"最佳产品: {best['asin']} (WAPE: {best['WAPE']:.2f}%)")
    print(f"最差产品: {worst['asin']} (WAPE: {worst['WAPE']:.2f}%)")
