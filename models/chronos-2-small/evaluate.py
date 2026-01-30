#!/usr/bin/env python3
"""
Chronos-2-Small 模型评估脚本
使用回测方法评估模型准确率
"""
import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline

def evaluate_model(
    data_path,
    model_path=None,
    marketplace='US',
    cutoff_date='2025-11-30',
    prediction_length=60,
    max_skus=100
):
    """
    评估模型准确率
    
    Args:
        data_path: 销量历史数据路径
        model_path: 微调模型路径 (None则使用预训练模型)
        marketplace: 站点
        cutoff_date: 回测截止日期
        prediction_length: 预测天数
        max_skus: 最大评估SKU数
    
    Returns:
        dict: 评估指标
    """
    # 加载数据
    df = pd.read_csv(data_path, parse_dates=['date'])
    df = df[df['marketplace'] == marketplace].copy()
    
    # 加载模型
    if model_path:
        print(f"加载微调模型: {model_path}")
        pipe = Chronos2Pipeline.from_pretrained(model_path, device_map="cuda", dtype=torch.float32)
    else:
        print("加载预训练模型: autogluon/chronos-2-small")
        pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda", dtype=torch.float32)
    
    # 准备测试数据
    cutoff = pd.to_datetime(cutoff_date)
    end_date = cutoff + pd.Timedelta(days=prediction_length)
    
    actual_totals = {}
    histories = {}
    
    for sku in df[df['date'] > cutoff]['sku'].unique()[:max_skus]:
        sku_data = df[df['sku'] == sku].sort_values('date')
        hist = sku_data[sku_data['date'] <= cutoff]['sales_quantity'].values
        actual = sku_data[(sku_data['date'] > cutoff) & (sku_data['date'] <= end_date)]['sales_quantity'].sum()
        
        if len(hist) >= 60 and actual > 0:
            histories[sku] = hist
            actual_totals[sku] = actual
    
    print(f"评估SKU数: {len(histories)}")
    
    # 预测
    predictions = {}
    for sku, hist in histories.items():
        tensor = torch.tensor(hist, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        forecast = pipe.predict(tensor, prediction_length=prediction_length)
        # 取中位数 (quantile index 6 = 0.5)
        pred_total = forecast[0][0, 6, :].sum().item()
        predictions[sku] = max(0, pred_total)
    
    # 计算指标
    total_actual = sum(actual_totals.values())
    total_pred = sum(predictions.values())
    total_error = sum(abs(actual_totals[s] - predictions[s]) for s in histories)
    
    wape = total_error / total_actual * 100
    accuracy = 100 - wape
    bias = (total_pred - total_actual) / total_actual * 100
    
    results = {
        'accuracy': accuracy,
        'wape': wape,
        'bias': bias,
        'total_actual': total_actual,
        'total_predicted': total_pred,
        'num_skus': len(histories)
    }
    
    print(f"\n评估结果:")
    print(f"  准确率: {accuracy:.1f}%")
    print(f"  WAPE: {wape:.1f}%")
    print(f"  偏差: {bias:+.1f}%")
    
    return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Chronos-2-Small 模型评估')
    parser.add_argument('--data', default='data/sales_history.csv', help='销量历史数据路径')
    parser.add_argument('--model', default=None, help='微调模型路径')
    parser.add_argument('--marketplace', default='US', help='站点')
    parser.add_argument('--cutoff', default='2025-11-30', help='回测截止日期')
    parser.add_argument('--days', type=int, default=60, help='预测天数')
    parser.add_argument('--max-skus', type=int, default=100, help='最大评估SKU数')
    
    args = parser.parse_args()
    evaluate_model(args.data, args.model, args.marketplace, args.cutoff, args.days, args.max_skus)
