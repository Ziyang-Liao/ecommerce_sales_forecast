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

## 数据维度说明

### 核心字段 (必需)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| sku | str | ⭐⭐⭐⭐⭐ | SKU编号 | 唯一标识每个产品，用于分组预测 |
| date | datetime | ⭐⭐⭐⭐⭐ | 日期 | 时间序列的时间维度，必须连续 |
| sales_quantity | int | ⭐⭐⭐⭐⭐ | 销售数量 | **预测目标**，模型的核心输入 |
| marketplace | str | ⭐⭐⭐⭐ | 站点 | 不同站点销售模式不同，需分开预测 |

### 价格相关 (强烈建议)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| sale_price | float | ⭐⭐⭐⭐ | 售价 | 价格变动直接影响销量，可作为协变量 |
| original_price | float | ⭐⭐⭐ | 原价 | 用于计算折扣力度 |
| discount_rate | float | ⭐⭐⭐⭐ | 折扣率 | 促销力度的量化指标，影响销量波动 |

### 广告相关 (建议)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| ad_spend | float | ⭐⭐⭐⭐ | 广告花费 | 广告投入与销量强相关 |
| ad_impressions | int | ⭐⭐⭐ | 广告曝光 | 反映产品曝光度 |
| ad_clicks | int | ⭐⭐⭐ | 广告点击 | 反映用户兴趣度 |

### 促销活动 (建议)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| is_lightning_deal | int | ⭐⭐⭐⭐ | 秒杀活动 | 秒杀期间销量会大幅波动 |
| is_coupon_active | int | ⭐⭐⭐ | 优惠券 | 优惠券影响转化率 |
| is_deal_of_day | int | ⭐⭐⭐ | 每日特惠 | 特惠活动影响销量 |

### 库存相关 (建议)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| fba_inventory | int | ⭐⭐⭐⭐ | FBA库存 | 缺货会导致销量为0，需要识别 |

### 产品表现 (可选)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| bsr_rank | int | ⭐⭐⭐ | BSR排名 | 反映产品竞争力变化 |
| rating | float | ⭐⭐ | 评分 | 评分影响转化率 |
| review_count | int | ⭐⭐ | 评论数 | 评论数影响购买决策 |

### 产品属性 (可选)

| 字段 | 类型 | 重要程度 | 说明 | 为什么需要 |
|------|------|----------|------|------------|
| asin | str | ⭐⭐ | Amazon产品ID | 产品唯一标识 |
| product_line | str | ⭐⭐ | 产品线 | 不同产品线季节性不同 |
| launch_date | datetime | ⭐⭐ | 上架日期 | 新品期销量模式特殊 |

### 重要程度说明

| 等级 | 含义 | 建议 |
|------|------|------|
| ⭐⭐⭐⭐⭐ | 必需 | 缺少则无法预测 |
| ⭐⭐⭐⭐ | 强烈建议 | 显著提升预测准确率 |
| ⭐⭐⭐ | 建议 | 有助于捕捉特殊事件 |
| ⭐⭐ | 可选 | 锦上添花 |

### 当前模型使用情况

**Chronos-2-Small 当前仅使用 `sales_quantity` 作为输入**，属于单变量预测。

未来可扩展为多变量预测，将价格、广告、促销等作为协变量输入，进一步提升准确率。

```python
# 当前使用方式 (单变量)
history = df['sales_quantity'].values
forecast = pipe.predict(history, prediction_length=60)

# 未来可扩展 (多变量 + 协变量)
task = {
    'target': sales_quantity,  # 预测目标
    'past_covariates': {       # 历史协变量
        'price': price_history,
        'ad_spend': ad_history,
    },
    'future_covariates': {     # 已知未来协变量
        'price': planned_price,
    }
}
forecast = pipe.predict([task], prediction_length=60)
```

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
