# Chronos-T5-Small 销量预测

基于 Amazon Chronos-T5-Small 预训练时序模型的销量预测方案，支持微调。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型名称 | amazon/chronos-t5-small |
| 参数量 | 46M |
| 架构 | T5 Encoder-Decoder |
| 特点 | 支持微调，采样式预测 |

## 性能对比

60天销量预测准确率 (100个SKU回测):

| 模型 | 准确率 | WAPE |
|------|--------|------|
| chronos-t5-small (预训练) | 55.7% | 44.3% |
| chronos-t5-small (微调后) | 82.9% | 17.1% |

## 环境要求

```bash
pip install chronos-forecasting torch pandas numpy gluonts
```

## 使用方法

### 1. 模型微调

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
```

### 2. 评估微调模型

```bash
python eval_finetuned.py
```

## 代码示例

### 预测

```python
import torch
from chronos import ChronosPipeline

# 加载模型 (预训练或微调后)
pipe = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",  # 或微调模型路径
    device_map="cuda",
    dtype=torch.float32
)

# 预测
history = torch.tensor([100, 120, 115, 130, ...], dtype=torch.float32)
forecast = pipe.predict(history, prediction_length=60, num_samples=20)

# 获取中位数
median = forecast.median(dim=1).values
```

## 注意事项

1. 微调可显著提升准确率 (55.7% → 82.9%)
2. 需要准备Arrow格式训练数据
3. 推荐使用GPU进行微调

## 参考资料

- [Chronos 论文](https://arxiv.org/abs/2403.07815)
- [HuggingFace 模型页](https://huggingface.co/amazon/chronos-t5-small)
