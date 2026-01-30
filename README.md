# E-commerce Sales Forecasting

Sales forecasting solution based on Amazon Chronos-2 pre-trained time series model.

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
│       ├── finetune_chronos.py
│       ├── finetune_config.yaml
│       ├── eval_finetuned.py
│       └── README.md
├── data/
│   ├── sales_history.csv         # Sales history data
│   ├── sku_metadata.csv          # SKU metadata
│   └── data_dictionary.md        # Data dictionary
├── src/
│   ├── generate_sample_data.py   # Sample data generator
│   ├── preprocess/
│   │   ├── preprocess.py         # Data preprocessing
│   │   └── add_features.py       # Feature engineering
│   └── evaluate/
│       └── evaluate.py           # Evaluation utilities
├── notebooks/
│   ├── deploy_chronos.ipynb      # SageMaker deployment
│   ├── batch_inference.ipynb     # Batch inference
│   └── evaluate.ipynb            # Evaluation visualization
├── tests/
│   └── test_covariate_impact.py  # Covariate impact testing
└── README.md
```

## Model Comparison

60-day sales forecast accuracy (100 SKUs backtesting):

| Model | Parameters | Accuracy | WAPE | Recommended Use |
|-------|------------|----------|------|-----------------|
| **chronos-2-small** | 28M | **92.2%** | 7.8% | ⭐ Production |
| chronos-t5-small (fine-tuned) | 46M | 82.9% | 17.1% | Customization needed |
| chronos-t5-small (pretrained) | 46M | 55.7% | 44.3% | Quick validation |
| chronos-bolt-small | 48M | 70.7% | 29.3% | Speed priority |

## Covariate Testing Conclusions

### Mature vs New Product Forecasting Strategy

| Scenario | Sales Only | Sales + Major Sale | Recommendation |
|----------|------------|-------------------|----------------|
| **Mature Products** (history ≥60 days) | 92.0% | 92.1% | Add major sale field |
| **New Products** (history <60 days) | 48.0% | 51.1% | Add major sale field |

### Key Findings

1. **Pretrained model is optimal**: Fine-tuning reduces accuracy for both mature and new products
2. **Fewer covariates is better**: Adding too many features introduces noise
3. **New product exception**: With insufficient history, `is_major_sale_event` improves accuracy by +3.1%
4. **Unified approach**: `Sales + is_major_sale_event` works for all scenarios

### Detailed Covariate Testing (Mature Products)

| Configuration | Accuracy |
|---------------|----------|
| No covariates | 92.0% |
| is_major_sale_event | **92.1%** |
| 6 promotion fields | 81.9% |
| All 18 covariates | 81.1% |

## CPU vs GPU Performance

### Speed Comparison

| Scenario | GPU | CPU | Winner |
|----------|-----|-----|--------|
| Single SKU | 49ms | 27ms | CPU |
| 100 SKUs batch | 14ms/SKU | 24ms/SKU | GPU (1.7x faster) |

### Accuracy Comparison

| Scenario | GPU | CPU | Difference |
|----------|-----|-----|------------|
| Mature Products | 71.25% | 71.25% | 0.00% |
| New Products | 48.02% | 48.02% | 0.00% |

**GPU and CPU produce identical results - no accuracy difference.**

### Recommendation

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| **Prediction only** | CPU | Same accuracy, lower cost |
| **Fine-tuning** | GPU | Much faster training |
| **Batch prediction (1000+ SKUs)** | GPU | Better throughput |

## Quick Start

### Environment Setup

```bash
pip install chronos-forecasting>=2.1.0 torch pandas numpy
```

### Using Chronos-2-Small (Recommended)

```bash
cd models/chronos-2-small

# Batch prediction
python predict.py --data ../../data/sales_history.csv --output forecast.csv --days 60

# Model evaluation
python evaluate.py --data ../../data/sales_history.csv --cutoff 2025-11-30
```

### CPU vs GPU Usage

```python
from chronos.chronos2 import Chronos2Pipeline

# GPU (for fine-tuning or large batch)
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cuda")

# CPU (for prediction, lower cost)
pipe = Chronos2Pipeline.from_pretrained("autogluon/chronos-2-small", device_map="cpu")
```

## Data Format

### Input Data (sales_history.csv)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| sku | str | ✅ | SKU identifier |
| date | datetime | ✅ | Date |
| sales_quantity | int | ✅ | Sales quantity |
| marketplace | str | ✅ | Marketplace (US/UK/DE etc.) |
| is_major_sale_event | int | Recommended | Major sale flag (for new products) |

### Output Data

| Field | Description |
|-------|-------------|
| sku | SKU identifier |
| date | Forecast date |
| predicted_median | Median prediction |
| predicted_p10 | 10th percentile (pessimistic) |
| predicted_p90 | 90th percentile (optimistic) |

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| WAPE | Weighted Absolute Percentage Error | <15% Excellent |
| Accuracy | Accuracy (100-WAPE) | >85% Good |
| Bias | Forecast bias | Close to 0 |

## Deployment Recommendations

### Instance Selection

| Use Case | Instance Type | Notes |
|----------|---------------|-------|
| **Prediction (CPU)** | c8g.xlarge | Graviton4, best price-performance |
| **Prediction (GPU)** | g5.xlarge | Large batch |
| **Fine-tuning** | g5.xlarge+ | GPU required |

### SageMaker Deployment

See `notebooks/deploy_chronos.ipynb` for endpoint deployment.

## References

- [Chronos-2 Paper](https://arxiv.org/abs/2510.15821)
- [Chronos Paper](https://arxiv.org/abs/2403.07815)
- [GitHub Repository](https://github.com/amazon-science/chronos-forecasting)
