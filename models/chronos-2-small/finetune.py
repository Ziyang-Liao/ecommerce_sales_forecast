#!/usr/bin/env python3
"""
Chronos-2-Small 微调脚本
使用自有数据微调 autogluon/chronos-2-small 模型
"""
import pandas as pd
import numpy as np
import torch
from chronos.chronos2 import Chronos2Pipeline
from pathlib import Path

def prepare_training_data(data_path, marketplace='US', min_history=60):
    """
    准备训练数据
    
    Args:
        data_path: 销量历史数据路径
        marketplace: 站点筛选
        min_history: 最小历史长度
    
    Returns:
        list: 训练数据列表
    """
    df = pd.read_csv(data_path, parse_dates=['date'])
    df = df[df['marketplace'] == marketplace].copy()
    
    train_data = []
    for sku in df['sku'].unique():
        sku_data = df[df['sku'] == sku].sort_values('date')
        history = sku_data['sales_quantity'].values.astype(np.float32)
        
        if len(history) >= min_history:
            train_data.append(torch.tensor(history))
    
    print(f"准备了 {len(train_data)} 个SKU的训练数据")
    return train_data

def finetune(
    data_path,
    output_dir='chronos2_finetuned',
    marketplace='US',
    prediction_length=60,
    num_steps=1000,
    learning_rate=1e-6,
    batch_size=32,
    finetune_mode='full'  # 'full' 或 'lora'
):
    """
    微调Chronos-2-Small模型
    
    Args:
        data_path: 训练数据路径
        output_dir: 模型输出目录
        marketplace: 站点
        prediction_length: 预测长度
        num_steps: 训练步数
        learning_rate: 学习率
        batch_size: 批次大小
        finetune_mode: 微调模式 ('full' 或 'lora')
    
    Returns:
        Chronos2Pipeline: 微调后的模型
    """
    # 准备数据
    train_data = prepare_training_data(data_path, marketplace)
    
    # 加载预训练模型
    print("加载预训练模型...")
    pipe = Chronos2Pipeline.from_pretrained(
        "autogluon/chronos-2-small",
        device_map="cuda",
        dtype=torch.float32
    )
    
    # 微调
    print(f"开始微调 (mode={finetune_mode}, steps={num_steps})...")
    finetuned_pipe = pipe.fit(
        inputs=train_data,
        prediction_length=prediction_length,
        num_steps=num_steps,
        learning_rate=learning_rate,
        batch_size=batch_size,
        finetune_mode=finetune_mode,
        output_dir=output_dir,
    )
    
    print(f"微调完成，模型已保存到: {output_dir}")
    return finetuned_pipe

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Chronos-2-Small 微调')
    parser.add_argument('--data', default='data/sales_history.csv', help='训练数据路径')
    parser.add_argument('--output', default='chronos2_finetuned', help='模型输出目录')
    parser.add_argument('--marketplace', default='US', help='站点')
    parser.add_argument('--steps', type=int, default=1000, help='训练步数')
    parser.add_argument('--lr', type=float, default=1e-6, help='学习率')
    parser.add_argument('--batch-size', type=int, default=32, help='批次大小')
    parser.add_argument('--mode', default='full', choices=['full', 'lora'], help='微调模式')
    
    args = parser.parse_args()
    finetune(
        args.data, args.output, args.marketplace,
        num_steps=args.steps, learning_rate=args.lr,
        batch_size=args.batch_size, finetune_mode=args.mode
    )
