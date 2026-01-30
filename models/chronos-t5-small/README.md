# Chronos-T5-Small Sales Forecasting

Sales forecasting solution based on Amazon Chronos-T5-Small pretrained time series model.

## Model Information

| Property | Value |
|----------|-------|
| Model Name | amazon/chronos-t5-small |
| Parameters | 46M |
| Architecture | T5 Encoder-Decoder |
| Features | Supports fine-tuning, sampling-based prediction |

## Performance Test Results

### Model Comparison (60-day forecast, 100 SKUs)

| Model | Accuracy | WAPE | Notes |
|-------|----------|------|-------|
| chronos-2-small (pretrained) | **92.2%** | 7.8% | ⭐ Recommended |
| **chronos-t5-small (fine-tuned)** | **82.9%** | 17.1% | This model |
| chronos-t5-small (pretrained) | 55.7% | 44.3% | Before fine-tuning |

### Fine-tuning Effect

| Status | Accuracy | Improvement |
|--------|----------|-------------|
| Pretrained | 55.7% | - |
| Fine-tuned 1000 steps | 82.9% | +27.2% |

**Conclusion: T5-Small requires fine-tuning for good results, but still underperforms Chronos-2-Small pretrained model.**

## Comparison with Chronos-2-Small

| Aspect | Chronos-T5-Small | Chronos-2-Small |
|--------|------------------|-----------------|
| Pretrained accuracy | 55.7% | **92.2%** |
| Fine-tuned accuracy | 82.9% | 88.8% (decreases) |
| Fine-tuning needed | ✅ Yes | ❌ No |
| Fine-tuning time | ~10 minutes | - |
| Recommendation | Alternative | ⭐ Primary choice |

**Recommendation: Use Chronos-2-Small pretrained model first - achieves 92.2% accuracy without fine-tuning.**

## Requirements

```bash
pip install chronos-forecasting torch pandas numpy gluonts
```

## Usage

### 1. Prepare Training Data

Convert data to Arrow format:

```python
import pandas as pd
from gluonts.dataset.arrow import ArrowWriter

df = pd.read_csv('data/sales_history.csv', parse_dates=['date'])

# Convert to GluonTS format
data = []
for sku in df['sku'].unique():
    sku_data = df[df['sku'] == sku].sort_values('date')
    data.append({
        'start': sku_data['date'].min(),
        'target': sku_data['sales_quantity'].values.tolist()
    })

# Save as Arrow format
ArrowWriter(compression='lz4').write_to_file(data, 'train_data/sales.arrow')
```

### 2. Fine-tune Model

```bash
python finetune_chronos.py
```

Configuration file `finetune_config.yaml`:
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

### 3. Evaluate Fine-tuned Model

```bash
python eval_finetuned.py
```

## Code Example

### Prediction with Pretrained Model

```python
import torch
from chronos import ChronosPipeline

# Load model
pipe = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cuda",
    dtype=torch.float32
)

# Predict
history = torch.tensor([100, 120, 115, 130, ...], dtype=torch.float32)
forecast = pipe.predict(history, prediction_length=60, num_samples=20)

# Get median
# forecast shape: (batch, num_samples, pred_len)
median = forecast.median(dim=1).values
print(f"Forecast total: {median.sum():.0f}")
```

### Prediction with Fine-tuned Model

```python
# Load fine-tuned model
pipe = ChronosPipeline.from_pretrained(
    "chronos_finetuned/checkpoint-1000",
    device_map="cuda",
    dtype=torch.float32
)

# Same prediction method
forecast = pipe.predict(history, prediction_length=60, num_samples=20)
```

## Fine-tuning Parameters

| Parameter | Recommended | Description |
|-----------|-------------|-------------|
| context_length | 512 | Context length |
| prediction_length | 64 | Prediction length |
| max_steps | 1000 | Training steps |
| learning_rate | 1e-4 | Learning rate |
| batch_size | 4 | Batch size |
| gradient_accumulation | 2 | Gradient accumulation |

## Notes

1. **Fine-tuning required**: Pretrained accuracy only 55.7%, must fine-tune
2. **Data format**: Requires Arrow format conversion
3. **Training time**: ~10 minutes for 1000 steps (GPU)
4. **VRAM requirement**: ~4GB

## References

- [Chronos Paper](https://arxiv.org/abs/2403.07815)
- [HuggingFace Model Page](https://huggingface.co/amazon/chronos-t5-small)
- [Training Script Documentation](https://github.com/amazon-science/chronos-forecasting/tree/main/scripts/training)
