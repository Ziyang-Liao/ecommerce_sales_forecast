# Chronos-2-Small 销量预测

基于 Amazon Chronos-2-Small 预训练时序模型的销量预测方案。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型名称 | autogluon/chronos-2-small |
| 参数量 | 28M |
| 架构 | T5 Encoder + Group Attention |
| 上下文长度 | 8192 |
| 输出分位数 | 13个 (0.01~0.99) |
| 特点 | 支持单变量/多变量/协变量预测 |

## 性能测试结果

### 模型对比 (60天预测, 100个SKU)

| 模型 | 参数量 | 准确率 | WAPE |
|------|--------|--------|------|
| **chronos-2-small (预训练)** | 28M | **92.2%** | 7.8% |
| chronos-t5-small (微调后) | 46M | 82.9% | 17.1% |
| chronos-bolt-small | 48M | 70.7% | 29.3% |
| chronos-t5-small (预训练) | 46M | 55.7% | 44.3% |

### 微调实验结论

我们在电商销量数据上进行了多组微调实验，结论是：**预训练模型效果最好，微调反而降低准确率**。

| 配置 | 训练Loss | 准确率 | 结论 |
|------|----------|--------|------|
| 预训练 (基准) | - | **92.2%** | ⭐ 最佳 |
| lr=1e-7, steps=200, batch=64 | 3.58→3.55 | 84.2% | ↓8% |
| lr=5e-7, steps=300, batch=64 | 3.37→2.89 | 75.6% | ↓17% |
| lr=1e-6, steps=200, batch=128 | 3.12→2.59 | 82.1% | ↓10% |
| lr=1e-6, steps=500, batch=32 | 3.64→2.87 | 88.8% | ↓3% |

**原因分析：**
1. Chronos-2 在大规模时序数据上预训练，泛化能力极强
2. 电商销量的季节性、趋势等模式已被预训练数据覆盖
3. 微调容易过拟合到训练数据的特定模式，损失泛化能力

**建议：直接使用预训练模型，无需微调。**

## 测试数据说明

| 指标 | 值 |
|------|-----|
| 总记录数 | 355,377 |
| SKU数量 | 787 |
| 时间跨度 | 760天 (约2年) |
| 站点 | US |
| 测试方法 | 回测 (cutoff: 2025-11-30) |
| 预测周期 | 60天 |
| 评估SKU数 | 100个 |

## 环境要求

```bash
# Python 3.10+
pip install chronos-forecasting>=2.1.0 torch pandas numpy

# GPU支持 (推荐)
# CUDA 11.8+ / 显存 >= 2GB
```

## 使用方法

### 1. 批量预测

```bash
python predict.py --data ../../data/sales_history.csv --output forecast.csv --days 60
```

参数说明:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| --data | data/sales_history.csv | 销量历史数据路径 |
| --output | forecast.csv | 预测结果输出路径 |
| --marketplace | US | 站点筛选 |
| --days | 60 | 预测天数 |

### 2. 模型评估 (回测)

```bash
python evaluate.py --data ../../data/sales_history.csv --cutoff 2025-11-30 --days 60
```

参数说明:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| --data | data/sales_history.csv | 销量历史数据路径 |
| --model | None | 微调模型路径 (不指定则用预训练) |
| --cutoff | 2025-11-30 | 回测截止日期 |
| --days | 60 | 预测天数 |
| --max-skus | 100 | 最大评估SKU数 |

### 3. 模型微调 (不推荐)

```bash
python finetune.py --data ../../data/sales_history.csv --output chronos2_finetuned --steps 500
```

⚠️ **注意：根据实验结果，微调会降低准确率，建议直接使用预训练模型。**

## 代码示例

### 单SKU预测

```python
import torch
from chronos.chronos2 import Chronos2Pipeline

# 加载模型
pipe = Chronos2Pipeline.from_pretrained(
    "autogluon/chronos-2-small",
    device_map="cuda",
    dtype=torch.float32
)

# 准备历史数据 (至少60天)
history = [100, 120, 115, 130, ...]  # 历史销量列表

# 预测
tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
forecast = pipe.predict(tensor, prediction_length=60)

# 获取中位数预测
# forecast[0] shape: (n_variates, n_quantiles, pred_len)
# quantiles: [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
# 中位数索引: 6 (对应0.5分位数)
median_forecast = forecast[0][0, 6, :].cpu().numpy()
print(f"未来60天预测销量: {median_forecast.sum():.0f}")
```

### 获取不同分位数预测

```python
# 分位数索引对照表
# 0: 0.01, 1: 0.05, 2: 0.1, 3: 0.2, 4: 0.3, 5: 0.4
# 6: 0.5 (中位数), 7: 0.6, 8: 0.7, 9: 0.8, 10: 0.9, 11: 0.95, 12: 0.99

p10 = forecast[0][0, 2, :]   # 10%分位数 (悲观预测)
p50 = forecast[0][0, 6, :]   # 50%分位数 (中位数)
p90 = forecast[0][0, 10, :]  # 90%分位数 (乐观预测)

print(f"悲观预测 (P10): {p10.sum():.0f}")
print(f"中位数预测 (P50): {p50.sum():.0f}")
print(f"乐观预测 (P90): {p90.sum():.0f}")
```

### 批量预测多个SKU

```python
import pandas as pd

# 加载数据
df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])

# 批量预测
results = []
for sku in df['sku'].unique():
    history = df[df['sku'] == sku].sort_values('date')['sales_quantity'].values
    if len(history) >= 60:
        tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        forecast = pipe.predict(tensor, prediction_length=60)
        pred_total = forecast[0][0, 6, :].sum().item()
        results.append({'sku': sku, 'predicted_60d': pred_total})

result_df = pd.DataFrame(results)
```

## 输出格式

预测结果CSV包含以下字段:

| 字段 | 类型 | 说明 |
|------|------|------|
| sku | str | SKU编号 |
| date | datetime | 预测日期 |
| predicted_median | float | 中位数预测 (P50) |
| predicted_p10 | float | 10%分位数预测 (悲观) |
| predicted_p90 | float | 90%分位数预测 (乐观) |

## 注意事项

1. **历史数据要求**: 建议至少60天历史数据，越长越好
2. **预测长度**: 建议不超过64天，更长预测建议使用滚动预测
3. **GPU内存**: 28M参数模型，约需2GB显存
4. **推理速度**: 单SKU预测约50ms (GPU)，支持批量预测
5. **数据预处理**: 模型内部会自动处理缺失值和标准化

## 参考资料

- [Chronos-2 技术报告](https://arxiv.org/abs/2510.15821)
- [HuggingFace 模型页](https://huggingface.co/autogluon/chronos-2-small)
- [GitHub 仓库](https://github.com/amazon-science/chronos-forecasting)
- [Amazon Science 博客](https://www.amazon.science/blog/introducing-chronos-2-from-univariate-to-universal-forecasting)
