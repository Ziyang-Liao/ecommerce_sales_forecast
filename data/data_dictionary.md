# 数据字典

本文档定义了销量预测系统的数据字段规范。

## 原始数据字段 (sales_history.csv)

| 字段名 | 中文名 | 类型 | 说明 |
|--------|--------|------|------|
| asin | Amazon产品ID | string | Amazon Standard Identification Number |
| sku | SKU编号 | string | 库存单位编号，唯一标识产品变体 |
| marketplace | 站点 | string | 销售站点 (US/UK/DE/FR/IT/ES/CA) |
| date | 日期 | datetime | 销售记录日期，格式 YYYY-MM-DD |
| sales_quantity | 销售数量 | int | 当日销售数量 |
| sale_price | 售价 | float | 当日实际售价 |
| original_price | 原价 | float | 标准零售价/划线价 |
| discount_rate | 折扣率 | float | 折扣力度，0.0~1.0 |
| ad_spend | 广告花费 | float | 当日广告投放花费 |
| ad_impressions | 广告曝光 | int | 当日广告展示次数 |
| ad_clicks | 广告点击 | int | 当日广告点击次数 |
| fba_inventory | FBA库存 | int | FBA仓库可售库存数量 |
| is_lightning_deal | 秒杀活动 | int | 是否参与Lightning Deal (0/1) |
| is_coupon_active | 优惠券 | int | 是否有优惠券生效 (0/1) |
| is_deal_of_day | 每日特惠 | int | 是否为Deal of the Day (0/1) |
| bsr_rank | BSR排名 | int | Best Seller Rank类目排名 |
| rating | 评分 | float | 产品平均评分 (1.0~5.0) |
| review_count | 评论数 | int | 累计评论数量 |
| product_line | 产品线 | string | 产品所属类别 |
| launch_date | 上架日期 | datetime | 产品首次上架日期 |

## 增强数据字段 (sales_history_enriched.csv)

在原始字段基础上，通过 `code_preprocess/add_features.py` 生成以下特征：

### 节假日/促销标记

| 字段名 | 中文名 | 说明 |
|--------|--------|------|
| is_prime_day | Prime Day | 7月15-17日 |
| is_prime_day_week | Prime Day周 | 7月12-20日 |
| is_prime_big_deal_days | Prime大促日 | 10月10-12日 |
| is_thanksgiving | 感恩节 | 11月第4个周四 |
| is_black_friday | 黑色星期五 | 感恩节后一天 |
| is_black_friday_week | 黑五周 | 感恩节前一周到网一后 |
| is_cyber_monday | 网络星期一 | 感恩节后的周一 |
| is_cyber_week | 网一周 | 网一后一周 |
| is_christmas_season | 圣诞季 | 11月15日-12月25日 |
| is_christmas | 圣诞节 | 12月25日 |
| is_christmas_rush | 圣诞冲刺 | 12月15-24日 |
| is_post_christmas | 节后促销 | 12月26-31日 |
| is_halloween | 万圣节 | 10月31日 |
| is_halloween_season | 万圣节季 | 10月1-31日 |
| is_back_to_school | 返校季 | 7月15日-9月15日 |
| is_valentines_week | 情人节周 | 2月7-14日 |
| is_mothers_day_week | 母亲节周 | 母亲节前一周 |
| is_fathers_day_week | 父亲节周 | 父亲节前一周 |
| is_labor_day_weekend | 劳动节周末 | 9月第1个周一及前两天 |
| is_memorial_day_weekend | 阵亡将士纪念日周末 | 5月最后一个周一及前两天 |
| is_independence_day_week | 独立日周 | 7月1-7日 |
| is_new_year_week | 新年周 | 1月1-7日 |
| is_easter_week | 复活节周 | 复活节前一周 |
| is_super_bowl_week | 超级碗周 | 超级碗前一周 |
| is_major_sale_event | 大促事件 | Prime Day/黑五/网一 |
| is_holiday_season | 节日季 | 圣诞季/万圣节季/返校季 |

### 时间特征

| 字段名 | 中文名 | 说明 |
|--------|--------|------|
| is_weekend | 周末 | 周六或周日 (0/1) |
| month | 月份 | 1-12 |
| day_of_week | 星期几 | 0-6 (周一到周日) |
| day_of_month | 日期 | 1-31 |
| week_of_year | 年周数 | 1-52 |
| quarter | 季度 | 1-4 |

### 产品生命周期

| 字段名 | 中文名 | 说明 |
|--------|--------|------|
| days_since_launch | 上架天数 | date - launch_date |
| product_lifecycle_stage | 生命周期阶段 | introduction/growth/maturity/decline/end_of_life |
| lifecycle_stage_code | 阶段编码 | 0-4 |
| is_new_product | 新品 | 上架≤90天 (0/1) |
| is_growth_stage | 成长期 | 上架91-365天 (0/1) |
| is_mature_product | 成熟期 | 上架366-730天 (0/1) |
| is_declining | 衰退期 | 上架>730天 (0/1) |

### 库存状态

| 字段名 | 中文名 | 说明 |
|--------|--------|------|
| is_out_of_stock | 缺货 | 库存=0 (0/1) |
| is_low_stock | 低库存 | 库存<50 (0/1) |

## 生命周期阶段定义

| 阶段 | 英文 | 上架天数 | 编码 |
|------|------|----------|------|
| 导入期 | introduction | 0-90天 | 0 |
| 成长期 | growth | 91-365天 | 1 |
| 成熟期 | maturity | 366-730天 | 2 |
| 衰退期 | decline | 731-1095天 | 3 |
| 淘汰期 | end_of_life | >1095天 | 4 |

## 数据示例

### 原始数据

```csv
sku,date,sales_quantity,marketplace,sale_price,discount_rate,fba_inventory,is_lightning_deal
LED-US-0001,2025-11-28,450,US,22.99,0.42,500,1
```

### 增强数据

```csv
sku,date,sales_quantity,is_black_friday,is_christmas_season,is_major_sale_event,days_since_launch,lifecycle_stage_code
LED-US-0001,2025-11-28,450,1,1,1,586,2
```
