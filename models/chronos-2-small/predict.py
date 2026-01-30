#!/usr/bin/env python3
"""
Chronos-2-Small 销量预测脚本
使用 autogluon/chronos-2-small 模型进行60天销量预测
"""
import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline
from datetime import datetime

def load_model(device="cuda"):
    """加载Chronos-2-Small模型"""
    return Chronos2Pipeline.from_pretrained(
        "autogluon/chronos-2-small",
        device_map=device,
        dtype=torch.float32
    )

def predict_sku(pipe, history, prediction_length=60):
    """
    预测单个SKU的销量
    
    Args:
        pipe: Chronos2Pipeline实例
        history: 历史销量数据 (numpy array)
        prediction_length: 预测天数
    
    Returns:
        dict: 包含各分位数预测结果
    """
    tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
    forecast = pipe.predict(tensor, prediction_length=prediction_length)
    
    # forecast[0] shape: (n_variates, n_quantiles, pred_len)
    # quantiles: [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    quantiles = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    
    result = {}
    for i, q in enumerate(quantiles):
        result[f'q{int(q*100):02d}'] = forecast[0][0, i, :].cpu().numpy()
    
    result['median'] = result['q50']
    return result

def batch_predict(data_path, output_path, marketplace='US', prediction_length=60):
    """
    批量预测所有SKU
    
    Args:
        data_path: 销量历史数据路径
        output_path: 预测结果输出路径
        marketplace: 站点筛选
        prediction_length: 预测天数
    """
    # 加载数据
    df = pd.read_csv(data_path, parse_dates=['date'])
    df = df[df['marketplace'] == marketplace].copy()
    
    # 加载模型
    pipe = load_model()
    
    # 获取最新日期作为预测起点
    max_date = df['date'].max()
    print(f"数据截止日期: {max_date}")
    print(f"预测天数: {prediction_length}")
    
    results = []
    skus = df['sku'].unique()
    
    for i, sku in enumerate(skus):
        sku_data = df[df['sku'] == sku].sort_values('date')
        history = sku_data['sales_quantity'].values
        
        if len(history) < 60:
            continue
        
        pred = predict_sku(pipe, history, prediction_length)
        
        # 生成预测日期
        pred_dates = pd.date_range(start=max_date + pd.Timedelta(days=1), periods=prediction_length)
        
        for j, date in enumerate(pred_dates):
            results.append({
                'sku': sku,
                'date': date,
                'predicted_median': pred['median'][j],
                'predicted_p10': pred['q10'][j],
                'predicted_p90': pred['q90'][j],
            })
        
        if (i + 1) % 50 == 0:
            print(f"已处理 {i+1}/{len(skus)} SKUs")
    
    # 保存结果
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_path, index=False)
    print(f"预测结果已保存到: {output_path}")
    
    return result_df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Chronos-2-Small 销量预测')
    parser.add_argument('--data', default='data/sales_history.csv', help='销量历史数据路径')
    parser.add_argument('--output', default='forecast_chronos2.csv', help='预测结果输出路径')
    parser.add_argument('--marketplace', default='US', help='站点')
    parser.add_argument('--days', type=int, default=60, help='预测天数')
    
    args = parser.parse_args()
    batch_predict(args.data, args.output, args.marketplace, args.days)
