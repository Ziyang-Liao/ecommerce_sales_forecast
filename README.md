# 跨境电商销量预测

基于 Amazon Chronos-2 预训练时序模型的销量预测方案。

## 项目结构

```
ecommerce_sales_forecast/
├── models/
│   ├── chronos-2-small/          # 推荐：准确率最高 (92.2%)
│   │   ├── predict.py            # 预测脚本
│   │   ├── evaluate.py           # 评估脚本
│   │   ├── finetune.py           # 微调脚本
│   │   └── README.md
│   └── chronos-t5-small/         # 支持微调
│       ├── finetune_chronos.py
│       ├── finetune_config.yaml
│       ├── eval_finetuned.py
│       └── README.md
├── data/
│   ├── sales_history.csv         # 销量历史数据
│   ├── sku_metadata.csv          # SKU元数据
│   └── data_dictionary.md        # 数据字典
├── src/
│   ├── generate_sample_data.py   # 模拟数据生成
│   ├── preprocess/
│   │   ├── preprocess.py         # 数据预处理
│   │   └── add_features.py       # 特征工程
│   └── evaluate/
│       └── evaluate.py           # 评估工具
├── notebooks/
│   ├── deploy_chronos.ipynb      # SageMaker部署
│   ├── batch_inference.ipynb     # 批量推理
│   └── evaluate.ipynb            # 评估可视化
├── tests/
│   └── test_covariate_impact.py  # 协变量测试
└── README.md
```

## 模型对比

60天销量预测准确率 (100个SKU回测):

| 模型 | 参数量 | 准确率 | WAPE | 推荐场景 |
|------|--------|--------|------|----------|
| **chronos-2-small** | 28M | **92.2%** | 7.8% | ⭐ 生产环境首选 |
| chronos-t5-small (微调) | 46M | 82.9% | 17.1% | 需要定制化 |
| chronos-t5-small (预训练) | 46M | 55.7% | 44.3% | 快速验证 |
| chronos-bolt-small | 48M | 70.7% | 29.3% | 追求速度 |

## 协变量测试结论

### 老品 vs 新品预测策略

| 场景 | 仅销量 | 销量+大促 | 建议 |
|------|--------|-----------|------|
| **老品** (历史≥60天) | 92.0% | 92.1% | 仅销量即可 |
| **新品** (历史<60天) | 48.0% | 51.1% | 加大促字段 |

### 关键发现

1. **预训练模型最优**：微调会降低准确率，无论老品还是新品
2. **协变量越少越好**：添加过多特征会引入噪声
3. **新品场景例外**：历史数据不足时，`is_major_sale_event` 可提升 +3.1%
4. **统一方案**：`销量 + is_major_sale_event` 适用于所有场景

### 协变量详细测试 (老品)

| 配置 | 准确率 |
|------|--------|
| 无协变量 | 92.0% |
| is_major_sale_event | **92.1%** |
| 6个促销字段 | 81.9% |
| 全部18个协变量 | 81.1% |

## 快速开始

### 环境准备

```bash
pip install chronos-forecasting>=2.1.0 torch pandas numpy
```

### 使用Chronos-2-Small预测 (推荐)

```bash
cd models/chronos-2-small

# 批量预测
python predict.py --data ../../data/sales_history.csv --output forecast.csv --days 60

# 模型评估
python evaluate.py --data ../../data/sales_history.csv --cutoff 2025-11-30
```

## 数据格式

### 输入数据 (sales_history.csv)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sku | str | ✅ | SKU编号 |
| date | datetime | ✅ | 日期 |
| sales_quantity | int | ✅ | 销售数量 |
| marketplace | str | ✅ | 站点 (US/UK/DE等) |
| is_major_sale_event | int | 建议 | 大促标记 (新品场景) |

### 输出数据

| 字段 | 说明 |
|------|------|
| sku | SKU编号 |
| date | 预测日期 |
| predicted_median | 中位数预测 |
| predicted_p10 | 10%分位数 (悲观) |
| predicted_p90 | 90%分位数 (乐观) |

## 评估指标

| 指标 | 说明 | 建议阈值 |
|------|------|----------|
| WAPE | 加权绝对百分比误差 | <15% 优秀 |
| Accuracy | 准确率 (100-WAPE) | >85% 良好 |
| Bias | 预测偏差 | 接近0 |

## 部署建议

### EC2实例选择

| 场景 | 实例类型 | 说明 |
|------|----------|------|
| 开发测试 | g5.xlarge | 24GB显存 |
| 生产环境 | g5.2xlarge | 批量预测 |
| 大规模 | g6e.xlarge | L40S GPU |

### SageMaker部署

参考 `notebooks/deploy_chronos.ipynb` 进行端点部署。

## 参考资料

- [Chronos-2 论文](https://arxiv.org/abs/2510.15821)
- [Chronos 论文](https://arxiv.org/abs/2403.07815)
- [GitHub 仓库](https://github.com/amazon-science/chronos-forecasting)
