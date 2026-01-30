"""
使用协变量的Chronos-2预测
"""
import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline

def predict_with_covariates(data_path, cutoff_date, pred_days=60, max_skus=100):
    """使用协变量进行预测"""
    
    df = pd.read_csv(data_path, parse_dates=['date', 'launch_date'])
    df_us = df[df['marketplace'] == 'US'].copy()
    
    cutoff = pd.to_datetime(cutoff_date)
    end_date = cutoff + pd.Timedelta(days=pred_days)
    
    # 加载模型
    pipe = Chronos2Pipeline.from_pretrained(
        "autogluon/chronos-2-small",
        device_map="cuda",
        dtype=torch.float32
    )
    
    # 协变量列表
    covariate_cols = [
        'discount_rate', 'ad_spend', 'is_lightning_deal', 
        'is_prime_day', 'is_black_friday', 'is_christmas_season',
        'is_halloween_season', 'days_since_launch', 'lifecycle_stage_code'
    ]
    
    # 准备测试数据
    results = {'sku': [], 'actual': [], 'pred_no_cov': [], 'pred_with_cov': []}
    
    test_skus = df_us[df_us['date'] > cutoff]['sku'].unique()[:max_skus]
    
    for i, sku in enumerate(test_skus):
        sku_data = df_us[df_us['sku'] == sku].sort_values('date')
        
        # 历史数据
        hist_data = sku_data[sku_data['date'] <= cutoff]
        if len(hist_data) < 60:
            continue
            
        # 实际销量
        future_data = sku_data[(sku_data['date'] > cutoff) & (sku_data['date'] <= end_date)]
        if len(future_data) == 0:
            continue
        actual = future_data['sales_quantity'].sum()
        
        # 方法1: 无协变量预测
        target = torch.tensor(hist_data['sales_quantity'].values, dtype=torch.float32)
        tensor = target.unsqueeze(0).unsqueeze(0)
        forecast = pipe.predict(tensor, prediction_length=pred_days)
        pred_no_cov = max(0, forecast[0][0, 6, :].sum().item())
        
        # 方法2: 有协变量预测
        # 准备协变量数据
        past_covs = {}
        for col in covariate_cols:
            if col in hist_data.columns:
                values = hist_data[col].fillna(0).values.astype(np.float32)
                past_covs[col] = torch.tensor(values)
        
        # 构建任务
        task = {
            'target': target,
            'past_covariates': past_covs,
        }
        
        try:
            forecast_cov = pipe.predict([task], prediction_length=pred_days)
            pred_with_cov = max(0, forecast_cov[0][0, 6, :].sum().item())
        except Exception as e:
            pred_with_cov = pred_no_cov  # 失败则用无协变量结果
        
        results['sku'].append(sku)
        results['actual'].append(actual)
        results['pred_no_cov'].append(pred_no_cov)
        results['pred_with_cov'].append(pred_with_cov)
        
        if (i + 1) % 20 == 0:
            print(f"已处理 {i+1}/{len(test_skus)}")
    
    # 计算准确率
    total_actual = sum(results['actual'])
    
    error_no_cov = sum(abs(a - p) for a, p in zip(results['actual'], results['pred_no_cov']))
    acc_no_cov = 100 - error_no_cov / total_actual * 100
    
    error_with_cov = sum(abs(a - p) for a, p in zip(results['actual'], results['pred_with_cov']))
    acc_with_cov = 100 - error_with_cov / total_actual * 100
    
    print(f"\n=== 结果对比 ({len(results['sku'])} SKUs) ===")
    print(f"无协变量准确率: {acc_no_cov:.1f}%")
    print(f"有协变量准确率: {acc_with_cov:.1f}%")
    
    return results

if __name__ == "__main__":
    predict_with_covariates('data/sales_history_enriched.csv', '2025-11-30', 60, 100)
