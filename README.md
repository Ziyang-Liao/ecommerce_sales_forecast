# 跨境电商销量预测

基于 Amazon Chronos 预训练时序模型的销量预测方案。

## 项目结构

```
ecommerce_sales_forecast/
├── models/
│   ├── chronos-2-small/      # 推荐：Chronos-2-Small模型 (准确率最高)
│   │   ├── predict.py        # 预测脚本
│   │   ├── finetune.py       # 微调脚本
│   │   ├── evaluate.py       # 评估脚本
│   │   └── README.md         # 使用说明
│   └── chronos-t5-small/     # Chronos-T5-Small模型 (支持微调)
│       ├── finetune_chronos.py
│       ├── finetune_config.yaml
│       ├── eval_finetuned.py
│       └── README.md
├── data/
│   ├── sales_history.csv     # 销量历史数据
│   └── sku_metadata.csv      # SKU元数据
├── code_preprocess/          # 数据预处理
├── code_evaluate/            # 评估工具
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

## 快速开始

### 环境准备

```bash
# Python 3.10+
pip install chronos-forecasting>=2.1.0 torch pandas numpy

# GPU支持 (推荐)
# 需要CUDA 11.8+
```

### 使用Chronos-2-Small预测 (推荐)

```bash
cd models/chronos-2-small

# 批量预测
python predict.py --data ../../data/sales_history.csv --output forecast.csv --days 60

# 模型评估
python evaluate.py --data ../../data/sales_history.csv --cutoff 2025-11-30
```

### 使用Chronos-T5-Small (需微调)

```bash
cd models/chronos-t5-small

# 微调模型
python finetune_chronos.py

# 评估
python eval_finetuned.py
```

## 数据格式

### 输入数据 (sales_history.csv)

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sku | str | ✅ | SKU编号 |
| date | datetime | ✅ | 日期 |
| sales_quantity | int | ✅ | 销售数量 |
| marketplace | str | ✅ | 站点 (US/UK/DE等) |

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
| 开发测试 | g5.xlarge | 24GB显存，性价比高 |
| 生产环境 | g5.2xlarge | 更大内存，批量预测 |
| 大规模 | g6e.xlarge | L40S GPU，最新架构 |

### SageMaker部署

参考 `deploy_chronos.ipynb` 进行SageMaker端点部署。

## 预测周期建议

| 场景 | 预测周期 | 更新频率 |
|------|----------|----------|
| 日常运营 | 14天 | 每日 |
| 备货计划 | 28天 | 每周 |
| 旺季规划 | 60天 | 每月 |

## 参考资料

- [Chronos-2 论文](https://arxiv.org/abs/2510.15821)
- [Chronos 论文](https://arxiv.org/abs/2403.07815)
- [GitHub 仓库](https://github.com/amazon-science/chronos-forecasting)
- [HuggingFace 模型](https://huggingface.co/collections/amazon/chronos-models-65f1791d630a8d57cb718444)
