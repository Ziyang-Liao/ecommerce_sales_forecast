# Chronos-T5-Small 销量预测

基于 Amazon Chronos-T5-Small 预训练时序模型的销量预测方案。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型名称 | amazon/chronos-t5-small |
| 参数量 | 46M |
| 架构 | T5 Encoder-Decoder |
| 特点 | 支持微调，采样式预测 |

## 性能测试结果

### 模型对比 (60天预测, 100个SKU)

| 模型 | 准确率 | WAPE | 说明 |
|------|--------|------|------|
| chronos-2-small (预训练) | **92.2%** | 7.8% | ⭐ 推荐 |
| **chronos-t5-small (微调后)** | **82.9%** | 17.1% | 本模型 |
| chronos-t5-small (预训练) | 55.7% | 44.3% | 微调前 |

### 微调效果

| 状态 | 准确率 | 提升 |
|------|--------|------|
| 预训练 | 55.7% | - |
| 微调1000步 | 82.9% | +27.2% |

**结论：T5-Small 需要微调才能达到较好效果，但仍不如 Chronos-2-Small 预训练模型。**

## 与 Chronos-2-Small 对比

| 对比项 | Chronos-T5-Small | Chronos-2-Small |
|--------|------------------|-----------------|
| 预训练准确率 | 55.7% | **92.2%** |
| 微调后准确率 | 82.9% | 88.8% (反而下降) |
| 是否需要微调 | ✅ 需要 | ❌ 不需要 |
| 微调时间 | ~10分钟 | - |
| 推荐程度 | 备选 | ⭐ 首选 |

**建议：优先使用 Chronos-2-Small 预训练模型，无需微调即可达到 92.2% 准确率。**

## 环境要求

```bash
pip install chronos-forecasting torch pandas numpy gluonts
```

## 使用方法

### 1. 准备训练数据

首先需要将数据转换为 Arrow 格式：

```python
import pandas as pd
from gluonts.dataset.arrow import ArrowWriter

df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])

# 转换为GluonTS格式
data = []
for sku in df['sku'].unique():
    sku_data = df[df['sku'] == sku].sort_values('date')
    data.append({
        'start': sku_data['date'].min(),
        'target': sku_data['sales_quantity'].values.tolist()
    })

# 保存为Arrow格式
ArrowWriter(compression='lz4').write_to_file(data, 'train_data/sales.arrow')
```

### 2. 模型微调

```bash
python finetune_chronos.py
```

配置文件 `finetune_config.yaml`:
```yaml
training_data_paths:
  - "train_data/sales.arrow"
context_length: 512
prediction_length: 64
max_steps: 1000
per_device_train_batch_size: 4
learning_rate: 0.0001
model_id: amazon/chronos-t5-small
model_type: seq2seq
random_init: false
```

### 3. 评估微调模型

```bash
python eval_finetuned.py
```

## 代码示例

### 使用预训练模型预测

```python
import torch
from chronos import ChronosPipeline

# 加载模型
pipe = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cuda",
    dtype=torch.float32
)

# 预测
history = torch.tensor([100, 120, 115, 130, ...], dtype=torch.float32)
forecast = pipe.predict(history, prediction_length=60, num_samples=20)

# 获取中位数
# forecast shape: (batch, num_samples, pred_len)
median = forecast.median(dim=1).values
print(f"预测总量: {median.sum():.0f}")
```

### 使用微调模型预测

```python
# 加载微调后的模型
pipe = ChronosPipeline.from_pretrained(
    "chronos_finetuned/checkpoint-1000",
    device_map="cuda",
    dtype=torch.float32
)

# 预测方式相同
forecast = pipe.predict(history, prediction_length=60, num_samples=20)
```

## 微调参数说明

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| context_length | 512 | 上下文长度 |
| prediction_length | 64 | 预测长度 |
| max_steps | 1000 | 训练步数 |
| learning_rate | 1e-4 | 学习率 |
| batch_size | 4 | 批次大小 |
| gradient_accumulation | 2 | 梯度累积 |

## 注意事项

1. **必须微调**: 预训练模型准确率仅55.7%，需要微调才能使用
2. **数据格式**: 需要转换为Arrow格式
3. **训练时间**: 1000步约需10分钟 (GPU)
4. **显存需求**: 约4GB

## 参考资料

- [Chronos 论文](https://arxiv.org/abs/2403.07815)
- [HuggingFace 模型页](https://huggingface.co/amazon/chronos-t5-small)
- [训练脚本文档](https://github.com/amazon-science/chronos-forecasting/tree/main/scripts/training)
