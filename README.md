# E-commerce Sales Forecasting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)

Sales forecasting solution based on Amazon Chronos-2 pre-trained time series model.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│  sales_history.csv  ──►  Preprocessing  ──►  Feature Engineering│
│                              │                      │           │
│                              ▼                      ▼           │
│                     sales_history_enriched.csv                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Chronos-2-Small Model                       │
├─────────────────────────────────────────────────────────────────┤
│  Input: Historical Sales + is_major_sale_event (optional)       │
│                               │                                 │
│                               ▼                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Tokenizer  │───►│  T5 Encoder │───►│  Quantile   │         │
│  │             │    │  + GroupAttn│    │  Decoder    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                               │                                 │
│                               ▼                                 │
│  Output: 13 Quantile Forecasts (p01, p05, ..., p50, ..., p99)  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Forecast Output                            │
├─────────────────────────────────────────────────────────────────┤
│  • Median prediction (p50)                                      │
│  • Confidence intervals (p10-p90)                               │
│  • Probabilistic forecasts for inventory planning               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Results

| Metric | Value |
|--------|-------|
| **Best Accuracy** | 92.2% (60-day forecast) |
| **Model** | chronos-2-small (28M params) |
| **Inference Speed** | 14ms/SKU (GPU), 24ms/SKU (CPU) |
| **Fine-tuning Required** | No |

## Project Structure

```
ecommerce_sales_forecast/
├── models/
│   ├── chronos-2-small/          # Recommended: Highest accuracy (92.2%)
│   │   ├── predict.py            # Prediction script
│   │   ├── evaluate.py           # Evaluation script
│   │   ├── finetune.py           # Fine-tuning script
│   │   └── README.md
│   └── chronos-t5-small/         # Supports fine-tuning
│       └── ...
├── data/
│   ├── sales_history.csv         # Sales history data
│   ├── sku_metadata.csv          # SKU metadata
│   └── data_dictionary.md        # Data dictionary
├── src/
│   ├── generate_sample_data.py   # Sample data generator
│   ├── preprocess/               # Data preprocessing
│   └── evaluate/                 # Evaluation utilities
├── notebooks/                    # Jupyter notebooks
├── tests/                        # Test scripts
├── requirements.txt
├── LICENSE
└── README.md
```

## Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce_sales_forecast.git
cd ecommerce_sales_forecast
pip install -r requirements.txt
```

### Basic Usage

```python
import torch
from chronos.chronos2 import Chronos2Pipeline

# Load model (CPU or GPU)
pipe = Chronos2Pipeline.from_pretrained(
    "autogluon/chronos-2-small",
    device_map="cpu"  # or "cuda" for GPU
)

# Prepare historical sales data
history = torch.tensor([100, 120, 115, 130, ...], dtype=torch.float32)

# Forecast next 60 days
forecast = pipe.predict(
    history.unsqueeze(0).unsqueeze(0),
    prediction_length=60
)

# Get median prediction
median = forecast[0][0, 6, :].numpy()
print(f"60-day forecast: {median.sum():.0f} units")
```

### Batch Prediction

```bash
cd models/chronos-2-small
python predict.py --data ../../data/sales_history.csv --output forecast.csv --days 60
```

## Model Comparison

| Model | Parameters | Accuracy | WAPE | Recommended Use |
|-------|------------|----------|------|-----------------|
| **chronos-2-small** | 28M | **92.2%** | 7.8% | ⭐ Production |
| chronos-t5-small (fine-tuned) | 46M | 82.9% | 17.1% | Customization needed |
| chronos-t5-small (pretrained) | 46M | 55.7% | 44.3% | Quick validation |
| chronos-bolt-small | 48M | 70.7% | 29.3% | Speed priority |

## Covariate Testing Conclusions

### Mature vs New Product Strategy

| Scenario | Sales Only | Sales + Major Sale | Recommendation |
|----------|------------|-------------------|----------------|
| **Mature Products** (≥60 days) | 92.0% | 92.1% | Add major sale field |
| **New Products** (<60 days) | 48.0% | 51.1% | Add major sale field |

### Key Findings

1. **Pretrained model is optimal** - Fine-tuning reduces accuracy
2. **Fewer covariates is better** - Too many features introduce noise
3. **Unified approach** - `Sales + is_major_sale_event` works for all scenarios

## CPU vs GPU Performance

| Scenario | GPU | CPU | Difference |
|----------|-----|-----|------------|
| Single SKU | 49ms | 27ms | CPU faster |
| 100 SKUs batch | 14ms/SKU | 24ms/SKU | GPU 1.7x faster |
| **Accuracy** | 92.2% | 92.2% | **Identical** |

### Recommendation

| Use Case | Instance | Notes |
|----------|----------|-------|
| **Prediction** | c8g.xlarge | Graviton4, best price-performance |
| **Fine-tuning** | g5.xlarge | GPU required |
| **Large batch** | g5.xlarge | Better throughput |

## Data Format

### Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sku | str | ✅ | SKU identifier |
| date | datetime | ✅ | Date |
| sales_quantity | int | ✅ | Sales quantity |
| marketplace | str | ✅ | Marketplace (US/UK/DE) |
| is_major_sale_event | int | Recommended | Major sale flag |

### Output

| Field | Description |
|-------|-------------|
| predicted_median | Median prediction (p50) |
| predicted_p10 | 10th percentile (pessimistic) |
| predicted_p90 | 90th percentile (optimistic) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## References

- [Chronos-2 Paper](https://arxiv.org/abs/2510.15821)
- [Chronos Paper](https://arxiv.org/abs/2403.07815)
- [GitHub Repository](https://github.com/amazon-science/chronos-forecasting)
- [HuggingFace Model](https://huggingface.co/autogluon/chronos-2-small)
