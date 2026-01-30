# 跨境电商销量预测

基于 Amazon Chronos-2 预训练时序模型的销量预测方案，部署在 SageMaker 上。

## 项目结构

```
ecommerce_sales_forecast/
├── code_preprocess/
│   └── preprocess.py      # 数据预处理与特征工程
├── code_evaluate/
│   └── evaluate.py        # 评估指标计算
├── deploy_chronos.ipynb   # 实时端点部署与预测
├── batch_inference.ipynb  # 多站点批量预测
├── evaluate.ipynb         # 模型评估与可视化
└── README.md
```

## 核心特征

### 节假日特征（影响最大）
| 特征 | 说明 | 影响程度 |
|------|------|----------|
| is_halloween_season | 万圣节季 (10月) | ⭐⭐⭐⭐⭐ |
| is_christmas_season | 圣诞季 (11.15-12.25) | ⭐⭐⭐⭐⭐ |
| is_black_friday_week | 黑五周 | ⭐⭐⭐⭐⭐ |
| is_prime_day | Prime Day | ⭐⭐⭐⭐ |
| is_back_to_school | 返校季 | ⭐⭐⭐ |

### 促销/广告特征
- discount_rate: 折扣率
- has_promotion: 是否有促销
- ad_spend: 广告花费
- has_advertising: 是否投放广告

### 产品生命周期
- days_since_launch: 上架天数
- is_new_product: 是否新品 (<60天)

## 使用方法

### 1. 实时预测 (单站点)
```bash
jupyter notebook deploy_chronos.ipynb
```

### 2. 批量预测 (多站点)
```bash
jupyter notebook batch_inference.ipynb
```

## 数据要求

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| asin | str | ✅ | Amazon 产品标识 |
| date | datetime | ✅ | 日期 |
| sales_quantity | int | ✅ | 销售数量 |
| sale_price | float | 建议 | 售价 |
| original_price | float | 建议 | 原价 |
| ad_spend | float | 建议 | 广告花费 |
| fba_inventory | int | 建议 | FBA 库存 |
| is_lightning_deal | int | 可选 | 秒杀活动 |
| is_coupon_active | int | 可选 | 优惠券 |
| launch_date | datetime | 可选 | 上架日期 |

## SageMaker 部署选项

| 模式 | 实例 | 适用场景 |
|------|------|----------|
| 实时端点 (GPU) | ml.g5.xlarge | 低延迟，高吞吐 |
| 实时端点 (CPU) | ml.c5.xlarge | 成本敏感 |
| Batch Transform | ml.c5.4xlarge | 大规模批量预测 |

## 预测周期建议

- 日常运营: 每日预测未来 14 天
- 备货计划: 每周预测未来 28 天
- 旺季前: 提前 60 天预测 Q4 销量

## 评估指标说明

| 指标 | 说明 | 建议阈值 |
|------|------|----------|
| MAE | 平均绝对误差 | 越小越好 |
| RMSE | 均方根误差 (对大误差敏感) | 越小越好 |
| MAPE | 平均绝对百分比误差 | <20% 良好 |
| WAPE | 加权绝对百分比误差 (推荐) | <15% 优秀 |
| Bias | 预测偏差 (正=高估, 负=低估) | 接近0 |
| QL | 分位数损失 | 越小越好 |

### 为什么推荐 WAPE？
- MAPE 对低销量产品误差放大
- WAPE 按销量加权，更符合业务实际
- 公式: WAPE = Σ|实际-预测| / Σ|实际|

## 业务影响分析

评估模块包含业务影响计算：
- **高估** → 库存积压成本
- **低估** → 缺货损失

帮助量化预测误差的实际业务成本。
