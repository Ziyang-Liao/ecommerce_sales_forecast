# Chronos-2-Small 销量预测

基于 Amazon Chronos-2-Small 预训练时序模型的销量预测方案。

## 模型信息

| 属性 | 值 |
|------|-----|
| 模型名称 | autogluon/chronos-2-small |
| 参数量 | 28M |
| 架构 | T5 Encoder + Group Attention |
| 最佳准确率 | **92.1%** (60天预测) |

## 协变量影响测试结果

我们测试了不同协变量组合对预测准确率的影响：

| 配置 | 字段数 | 准确率 | vs基准 | 结论 |
|------|--------|--------|--------|------|
| **无协变量 (基准)** | 1 | 92.0% | - | 基准线 |
| **只用大促标记** | 1 | **92.1%** | +0.1% | ✅ **最佳配置** |
| 只用上架天数 | 1 | 89.3% | -2.7% | ❌ 有害 |
| 只用生命周期编码 | 1 | 89.5% | -2.5% | ❌ 有害 |
| 只用折扣率 | 1 | 90.2% | -1.8% | ❌ 有害 |
| 生命周期组合 | 2 | 89.3% | -2.7% | ❌ 有害 |
| 节假日+促销 | 3 | 83.6% | -8.4% | ❌ 严重有害 |
| 节假日组合 | 3 | 68.0% | -24.0% | ❌ 严重有害 |
| 全部协变量 | 18 | 84.8% | -7.2% | ❌ 有害 |

### 关键发现

1. **Chronos-2 预训练模型已从销量序列学到季节性模式**
   - 模型能自动识别节假日、周期性等模式
   - 不需要显式告诉模型"这是圣诞季"

2. **添加过多协变量反而降低准确率**
   - 协变量引入噪声，干扰模型判断
   - 模型需要额外学习如何使用协变量

3. **只有简单的二值特征有微小提升**
   - `is_major_sale_event` (大促标记) 提升0.1%
   - 复杂特征组合反而有害

4. **推荐配置**
   - 使用 `is_major_sale_event` 单个协变量
   - 或直接不使用协变量 (准确率差异仅0.1%)

### 运行测试

```bash
python tests/test_covariate_impact.py
```

## 数据字段说明

### 实际使用的字段

| 字段 | 用途 | 重要程度 |
|------|------|----------|
| sales_quantity | 预测目标 | ⭐⭐⭐⭐⭐ 必需 |
| is_major_sale_event | 协变量 | ⭐⭐ 可选 (提升0.1%) |

### 生成但未使用的字段 (41个)

这些字段已生成到 `sales_history_enriched.csv`，但经测试发现对预测无帮助或有害：

**节假日字段** (对预测有害，模型已从销量学到)
- is_prime_day, is_prime_day_week, is_black_friday, is_black_friday_week
- is_cyber_monday, is_christmas_season, is_halloween_season 等

**生命周期字段** (对预测有害)
- days_since_launch, lifecycle_stage_code, is_new_product, is_declining 等

**时间字段** (对预测有害)
- month, day_of_week, quarter, week_of_year 等

**这些字段的价值**：
- 数据分析和可视化
- 业务理解和报表
- 后处理人工调整

## 使用方法

### 1. 数据准备

首先生成增强数据（添加节假日等特征）：

```bash
python code_preprocess/add_features.py
```

### 2. 批量预测

```bash
python models/chronos-2-small/predict.py \
    --data data/sales_history_enriched.csv \
    --output forecast.csv \
    --days 60
```

### 3. 模型评估

```bash
python models/chronos-2-small/evaluate.py \
    --data data/sales_history_enriched.csv \
    --cutoff 2025-11-30
```

### 4. 协变量影响测试

```bash
python tests/test_covariate_impact.py
```

## 代码示例

### 使用最佳配置预测

```python
import torch
import numpy as np
from chronos.chronos2 import Chronos2Pipeline

# 加载模型
pipe = Chronos2Pipeline.from_pretrained(
    "autogluon/chronos-2-small",
    device_map="cuda",
    dtype=torch.float32
)

# 历史销量
history = np.array([100, 120, 115, 130, ...])  # 至少60天

# 未来大促标记 (可选)
# 1表示大促日，0表示普通日
future_is_major_sale = np.array([0, 0, 1, 1, 0, ...])  # 长度=预测天数

# 预测
target = torch.tensor(history, dtype=torch.float32)

if future_is_major_sale is not None:
    task = {
        'target': target,
        'future_covariates': {
            'is_major_sale_event': torch.tensor(future_is_major_sale, dtype=torch.float32)
        }
    }
    forecast = pipe.predict([task], prediction_length=60)
else:
    tensor = target.unsqueeze(0).unsqueeze(0)
    forecast = pipe.predict(tensor, prediction_length=60)

# 获取中位数预测
median = forecast[0][0, 6, :].cpu().numpy()
print(f"未来60天预测总量: {median.sum():.0f}")
```

## 环境要求

```bash
pip install chronos-forecasting>=2.1.0 torch pandas numpy
```

## 参考资料

- [Chronos-2 技术报告](https://arxiv.org/abs/2510.15821)
- [HuggingFace 模型页](https://huggingface.co/autogluon/chronos-2-small)
- [GitHub 仓库](https://github.com/amazon-science/chronos-forecasting)
