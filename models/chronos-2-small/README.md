# Chronos-2-Small 销量预测

基于 Amazon Chronos-2-Small 预训练时序模型的销量预测方案。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型名称 | autogluon/chronos-2-small |
| 参数量 | 28M |
| 架构 | T5 Encoder + Group Attention |
| 特点 | 支持单变量/多变量/协变量预测 |

## 性能对比

60天销量预测准确率 (100个SKU回测):

| 模型 | 参数量 | 准确率 | WAPE |
|------|--------|--------|------|
| **chronos-2-small** | 28M | **92.2%** | 7.8% |
| chronos-t5-small | 46M | 82.8% | 17.2% |
| chronos-bolt-small | 48M | 70.7% | 29.3% |

## 环境要求

```bash
# Python 3.10+
pip install chronos-forecasting>=2.1.0 torch pandas numpy
```

## 使用方法

### 1. 批量预测

```bash
python predict.py --data data/sales_history.csv --output forecast.csv --days 60
```

参数说明:
- `--data`: 销量历史数据路径
- `--output`: 预测结果输出路径
- `--marketplace`: 站点筛选 (默认: US)
- `--days`: 预测天数 (默认: 60)

### 2. 模型评估

```bash
python evaluate.py --data data/sales_history.csv --cutoff 2025-11-30 --days 60
```

参数说明:
- `--data`: 销量历史数据路径
- `--model`: 微调模型路径 (可选，不指定则使用预训练模型)
- `--cutoff`: 回测截止日期
- `--days`: 预测天数
- `--max-skus`: 最大评估SKU数

### 3. 模型微调 (可选)

```bash
python finetune.py --data data/sales_history.csv --output chronos2_finetuned --steps 1000
```

参数说明:
- `--data`: 训练数据路径
- `--output`: 模型输出目录
- `--steps`: 训练步数 (默认: 1000)
- `--lr`: 学习率 (默认: 1e-6)
- `--batch-size`: 批次大小 (默认: 32)
- `--mode`: 微调模式 (full/lora)

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
history = [100, 120, 115, 130, ...]  # 历史销量

# 预测
tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
forecast = pipe.predict(tensor, prediction_length=60)

# 获取中位数预测 (quantile index 6 = 0.5)
median_forecast = forecast[0][0, 6, :].cpu().numpy()
print(f"未来60天预测销量: {median_forecast.sum():.0f}")
```

### 获取分位数预测

```python
# quantiles: [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
p10 = forecast[0][0, 2, :]   # 10%分位数
p50 = forecast[0][0, 6, :]   # 50%分位数 (中位数)
p90 = forecast[0][0, 10, :]  # 90%分位数
```

## 输出格式

预测结果CSV包含以下字段:

| 字段 | 说明 |
|------|------|
| sku | SKU编号 |
| date | 预测日期 |
| predicted_median | 中位数预测 |
| predicted_p10 | 10%分位数预测 |
| predicted_p90 | 90%分位数预测 |

## 注意事项

1. **历史数据要求**: 建议至少60天历史数据
2. **预测长度**: 建议不超过64天，更长预测可使用滚动预测
3. **GPU内存**: 28M参数模型，约需2GB显存
4. **推理速度**: 单SKU预测约50ms (GPU)

## 参考资料

- [Chronos-2 论文](https://arxiv.org/abs/2510.15821)
- [HuggingFace 模型页](https://huggingface.co/autogluon/chronos-2-small)
- [GitHub 仓库](https://github.com/amazon-science/chronos-forecasting)
