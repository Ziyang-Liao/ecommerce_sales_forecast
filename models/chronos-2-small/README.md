# Chronos-2-Small Sales Forecasting

Sales forecasting solution based on Amazon Chronos-2-Small pretrained time series model.

## Model Information

| Property | Value |
|----------|-------|
| Model Name | autogluon/chronos-2-small |
| Parameters | 28M |
| Architecture | T5 Encoder + Group Attention |
| Best Accuracy | **92.1%** (60-day forecast) |

## Covariate Impact Test Results

We tested the impact of different covariate combinations on forecast accuracy:

| Configuration | Fields | Accuracy | vs Baseline | Conclusion |
|---------------|--------|----------|-------------|------------|
| **No covariates (baseline)** | 1 | 92.0% | - | Baseline |
| **Major sale flag only** | 1 | **92.1%** | +0.1% | ✅ **Best config** |
| Days since launch only | 1 | 89.3% | -2.7% | ❌ Harmful |
| Lifecycle code only | 1 | 89.5% | -2.5% | ❌ Harmful |
| Discount rate only | 1 | 90.2% | -1.8% | ❌ Harmful |
| Lifecycle combination | 2 | 89.3% | -2.7% | ❌ Harmful |
| Holiday + promotion | 3 | 83.6% | -8.4% | ❌ Very harmful |
| Holiday combination | 3 | 68.0% | -24.0% | ❌ Very harmful |
| All covariates | 18 | 84.8% | -7.2% | ❌ Harmful |

### Key Findings

1. **Chronos-2 pretrained model already learned seasonality from sales data**
   - Model automatically identifies holidays, cyclical patterns
   - No need to explicitly tell the model "this is Christmas season"

2. **Adding too many covariates reduces accuracy**
   - Covariates introduce noise, interfering with model judgment
   - Model needs extra effort to learn how to use covariates

3. **Only simple binary features provide marginal improvement**
   - `is_major_sale_event` improves by 0.1%
   - Complex feature combinations are harmful

4. **Recommended configuration**
   - Use `is_major_sale_event` as single covariate
   - Or use no covariates (accuracy difference only 0.1%)

### Run Tests

```bash
python tests/test_covariate_impact.py
```

## Data Fields

### Fields Actually Used

| Field | Purpose | Importance |
|-------|---------|------------|
| sales_quantity | Prediction target | ⭐⭐⭐⭐⭐ Required |
| is_major_sale_event | Covariate | ⭐⭐ Optional (+0.1%) |

### Generated but Unused Fields (41)

These fields are generated in `sales_history_enriched.csv`, but testing shows they don't help or are harmful:

**Holiday fields** (harmful - model already learns from sales)
- is_prime_day, is_prime_day_week, is_black_friday, is_black_friday_week
- is_cyber_monday, is_christmas_season, is_halloween_season, etc.

**Lifecycle fields** (harmful)
- days_since_launch, lifecycle_stage_code, is_new_product, is_declining, etc.

**Time fields** (harmful)
- month, day_of_week, quarter, week_of_year, etc.

**Value of these fields**:
- Data analysis and visualization
- Business understanding and reporting
- Post-processing manual adjustments

## Usage

### 1. Data Preparation

First generate enriched data (add holiday features):

```bash
python src/preprocess/add_features.py
```

### 2. Batch Prediction

```bash
python models/chronos-2-small/predict.py \
    --data data/sales_history_enriched.csv \
    --output forecast.csv \
    --days 60
```

### 3. Model Evaluation

```bash
python models/chronos-2-small/evaluate.py \
    --data data/sales_history_enriched.csv \
    --cutoff 2025-11-30
```

## Code Example

### Prediction with Best Configuration

```python
import torch
import numpy as np
from chronos.chronos2 import Chronos2Pipeline

# Load model
pipe = Chronos2Pipeline.from_pretrained(
    "autogluon/chronos-2-small",
    device_map="cuda",
    dtype=torch.float32
)

# Historical sales
history = np.array([100, 120, 115, 130, ...])  # At least 60 days

# Prediction
tensor = torch.tensor(history, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
forecast = pipe.predict(tensor, prediction_length=60)

# Get median prediction
median = forecast[0][0, 6, :].cpu().numpy()
print(f"60-day forecast total: {median.sum():.0f}")
```

## Requirements

```bash
pip install chronos-forecasting>=2.1.0 torch pandas numpy
```

## References

- [Chronos-2 Technical Report](https://arxiv.org/abs/2510.15821)
- [HuggingFace Model Page](https://huggingface.co/autogluon/chronos-2-small)
- [GitHub Repository](https://github.com/amazon-science/chronos-forecasting)
