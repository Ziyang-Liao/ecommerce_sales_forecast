# 数据字典

本文档定义了销量预测系统所需的数据字段规范。

适用场景：Amazon北美/欧洲大卖家的销量预测。

---

## 字段总览

### 核心字段

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 1 | sku | SKU编号 | string | ✅ | ⭐⭐⭐⭐⭐ |
| 2 | date | 日期 | datetime | ✅ | ⭐⭐⭐⭐⭐ |
| 3 | sales_quantity | 销售数量 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 4 | marketplace | 站点 | string | ✅ | ⭐⭐⭐⭐⭐ |

### 节假日与促销日历 (极其重要)

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 5 | is_prime_day | Prime Day | int | ✅ | ⭐⭐⭐⭐⭐ |
| 6 | is_black_friday | 黑色星期五 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 7 | is_cyber_monday | 网络星期一 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 8 | is_christmas_season | 圣诞季 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 9 | is_thanksgiving | 感恩节 | int | 建议 | ⭐⭐⭐⭐ |
| 10 | is_easter | 复活节 | int | 建议 | ⭐⭐⭐⭐ |
| 11 | is_valentines | 情人节 | int | 建议 | ⭐⭐⭐ |
| 12 | is_mothers_day | 母亲节 | int | 建议 | ⭐⭐⭐ |
| 13 | is_fathers_day | 父亲节 | int | 建议 | ⭐⭐⭐ |
| 14 | is_halloween | 万圣节 | int | 建议 | ⭐⭐⭐⭐ |
| 15 | is_back_to_school | 返校季 | int | 建议 | ⭐⭐⭐ |
| 16 | is_labor_day | 劳动节 | int | 建议 | ⭐⭐⭐ |
| 17 | is_memorial_day | 阵亡将士纪念日 | int | 建议 | ⭐⭐⭐ |
| 18 | days_to_holiday | 距最近节假日天数 | int | 建议 | ⭐⭐⭐⭐ |
| 19 | holiday_name | 最近节假日名称 | string | 可选 | ⭐⭐ |

### 产品生命周期 (非常重要)

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 20 | launch_date | 上架日期 | datetime | ✅ | ⭐⭐⭐⭐⭐ |
| 21 | days_since_launch | 上架天数 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 22 | product_lifecycle_stage | 生命周期阶段 | string | 建议 | ⭐⭐⭐⭐⭐ |
| 23 | is_new_product | 是否新品 | int | 建议 | ⭐⭐⭐⭐ |
| 24 | is_mature_product | 是否成熟期 | int | 建议 | ⭐⭐⭐⭐ |
| 25 | is_declining_product | 是否衰退期 | int | 建议 | ⭐⭐⭐⭐ |
| 26 | has_newer_version | 是否有新版本 | int | 建议 | ⭐⭐⭐⭐ |
| 27 | newer_version_launch_date | 新版本上架日期 | datetime | 可选 | ⭐⭐⭐ |

### 促销活动

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 28 | is_lightning_deal | 秒杀活动 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 29 | is_deal_of_day | 每日特惠 | int | 建议 | ⭐⭐⭐⭐ |
| 30 | is_coupon_active | 优惠券 | int | 建议 | ⭐⭐⭐⭐ |
| 31 | is_best_deal | Best Deal | int | 建议 | ⭐⭐⭐⭐ |
| 32 | discount_rate | 折扣率 | float | ✅ | ⭐⭐⭐⭐⭐ |
| 33 | sale_price | 售价 | float | 建议 | ⭐⭐⭐⭐ |
| 34 | original_price | 原价 | float | 可选 | ⭐⭐⭐ |

### 广告投放

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 35 | ad_spend | 广告花费 | float | 建议 | ⭐⭐⭐⭐ |
| 36 | ad_impressions | 广告曝光 | int | 可选 | ⭐⭐⭐ |
| 37 | ad_clicks | 广告点击 | int | 可选 | ⭐⭐⭐ |

### 库存与运营

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 38 | fba_inventory | FBA库存 | int | ✅ | ⭐⭐⭐⭐⭐ |
| 39 | is_out_of_stock | 是否缺货 | int | 建议 | ⭐⭐⭐⭐ |
| 40 | days_of_inventory | 库存可售天数 | int | 可选 | ⭐⭐⭐ |

### 产品表现

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 41 | bsr_rank | BSR排名 | int | 建议 | ⭐⭐⭐⭐ |
| 42 | bsr_rank_change | BSR排名变化 | int | 可选 | ⭐⭐⭐ |
| 43 | rating | 评分 | float | 可选 | ⭐⭐⭐ |
| 44 | review_count | 评论数 | int | 可选 | ⭐⭐⭐ |
| 45 | review_count_change | 评论数变化 | int | 可选 | ⭐⭐ |

### 产品属性

| 序号 | 字段名 | 中文名 | 类型 | 必需 | 重要程度 |
|------|--------|--------|------|------|----------|
| 46 | asin | Amazon产品ID | string | 可选 | ⭐⭐ |
| 47 | product_line | 产品线 | string | 建议 | ⭐⭐⭐ |
| 48 | category | 类目 | string | 可选 | ⭐⭐ |

---

## 关键维度详细说明

### 一、节假日与促销日历

这是影响销量最大的因素之一。北美和欧洲的购物高峰期：

#### 北美重要节日/促销日

| 节日/促销 | 时间 | 销量影响 | 说明 |
|-----------|------|----------|------|
| **Prime Day** | 7月中旬 (2天) | ⭐⭐⭐⭐⭐ 暴增5-20倍 | Amazon最大促销日，必须标注 |
| **黑色星期五** | 11月第4个周五 | ⭐⭐⭐⭐⭐ 暴增5-15倍 | 年度最大购物日 |
| **网络星期一** | 黑五后的周一 | ⭐⭐⭐⭐⭐ 暴增3-10倍 | 线上购物高峰 |
| **圣诞季** | 11.15-12.25 | ⭐⭐⭐⭐⭐ 持续高位 | 全年销售占比30-40% |
| 感恩节 | 11月第4个周四 | ⭐⭐⭐⭐ 增长2-5倍 | 黑五前一天 |
| 万圣节 | 10.31 | ⭐⭐⭐⭐ 特定品类暴增 | 装饰/服装类影响大 |
| 返校季 | 8-9月 | ⭐⭐⭐ 增长1.5-3倍 | 学习用品/电子产品 |
| 情人节 | 2.14 | ⭐⭐⭐ 特定品类增长 | 礼品类影响大 |
| 母亲节 | 5月第2个周日 | ⭐⭐⭐ 礼品类增长 | |
| 父亲节 | 6月第3个周日 | ⭐⭐⭐ 礼品类增长 | |
| 劳动节 | 9月第1个周一 | ⭐⭐⭐ 促销日 | |
| 阵亡将士纪念日 | 5月最后一个周一 | ⭐⭐⭐ 促销日 | |

#### 欧洲重要节日

| 节日 | 时间 | 影响站点 |
|------|------|----------|
| 黑色星期五 | 11月第4个周五 | 全欧洲 |
| 圣诞季 | 11.15-12.25 | 全欧洲 |
| Boxing Day | 12.26 | UK |
| 德国统一日 | 10.3 | DE |
| 法国国庆 | 7.14 | FR |

#### 字段定义

**is_prime_day**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | ✅ 是 |
| 重要程度 | ⭐⭐⭐⭐⭐ |
| 枚举值 | 0 (否), 1 (是) |

**含义**: 当日是否为Prime Day。

**为什么极其重要**: 
- Prime Day销量可达平时的5-20倍
- 不标注会严重干扰模型学习
- 是全年最重要的销售事件之一

**days_to_holiday**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | 建议 |
| 重要程度 | ⭐⭐⭐⭐ |
| 范围 | -30 ~ 30 |

**含义**: 距离最近重要节假日的天数（负数表示节后）。

**为什么需要**: 
- 节前1-2周销量开始上升
- 节后销量快速回落
- 帮助模型学习节日效应的时间分布

---

### 二、产品生命周期

产品生命周期对销量趋势影响巨大，必须纳入考虑。

#### 生命周期阶段定义

| 阶段 | 上架天数 | 特征 | 销量趋势 |
|------|----------|------|----------|
| **导入期** | 0-90天 | 新品爬坡 | 📈 快速上升 |
| **成长期** | 90-365天 | 销量增长 | 📈 稳步上升 |
| **成熟期** | 1-2年 | 销量稳定 | ➡️ 平稳 |
| **衰退期** | 2-3年 | 销量下滑 | 📉 缓慢下降 |
| **淘汰期** | >3年 | 销量萎缩 | 📉 快速下降 |

#### 字段定义

**days_since_launch**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | ✅ 是 |
| 重要程度 | ⭐⭐⭐⭐⭐ |
| 计算 | date - launch_date |

**含义**: 产品上架至今的天数。

**为什么极其重要**: 
- 新品期(0-90天)销量模式特殊，需要爬坡
- 成熟期(1-2年)销量相对稳定
- 老品(>2年)销量会自然衰退
- 不考虑会导致预测严重偏差

**product_lifecycle_stage**
| 属性 | 值 |
|------|-----|
| 类型 | string |
| 必需 | 建议 |
| 重要程度 | ⭐⭐⭐⭐⭐ |
| 枚举值 | introduction, growth, maturity, decline, end_of_life |

**含义**: 产品当前所处的生命周期阶段。

**计算逻辑**:
```python
def get_lifecycle_stage(days_since_launch, has_newer_version):
    if days_since_launch <= 90:
        return 'introduction'  # 导入期
    elif days_since_launch <= 365:
        return 'growth'  # 成长期
    elif days_since_launch <= 730:  # 2年
        if has_newer_version:
            return 'decline'  # 有新版本，进入衰退
        return 'maturity'  # 成熟期
    elif days_since_launch <= 1095:  # 3年
        return 'decline'  # 衰退期
    else:
        return 'end_of_life'  # 淘汰期
```

**has_newer_version**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | 建议 |
| 重要程度 | ⭐⭐⭐⭐ |
| 枚举值 | 0 (否), 1 (是) |

**含义**: 是否已发布该产品的新版本/迭代款。

**为什么重要**: 
- 新版本发布后，老版本销量会加速下滑
- 部分用户会等待新品而暂缓购买
- 是判断产品是否进入衰退期的关键信号

---

### 三、促销活动

#### 字段定义

**is_lightning_deal**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | ✅ 是 |
| 重要程度 | ⭐⭐⭐⭐⭐ |

**含义**: 当日是否参与Lightning Deal秒杀。

**为什么极其重要**: 
- 秒杀期间销量暴增3-10倍
- 持续时间通常4-12小时
- 不标注会导致模型将其误判为趋势变化

**discount_rate**
| 属性 | 值 |
|------|-----|
| 类型 | float |
| 必需 | ✅ 是 |
| 重要程度 | ⭐⭐⭐⭐⭐ |
| 范围 | 0.0 ~ 0.8 |
| 计算 | 1 - sale_price / original_price |

**含义**: 当日折扣力度。

**为什么极其重要**: 
- 折扣率与销量增幅强相关
- 大促期间折扣率通常30-50%
- 是预测促销期销量的关键特征

---

### 四、库存约束

**fba_inventory**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | ✅ 是 |
| 重要程度 | ⭐⭐⭐⭐⭐ |

**含义**: 当日FBA仓库可售库存。

**为什么极其重要**: 
- **库存为0时销量必然为0**
- 需要区分"无需求"和"缺货"
- 缺货期间的0销量不应影响需求预测

**is_out_of_stock**
| 属性 | 值 |
|------|-----|
| 类型 | int |
| 必需 | 建议 |
| 重要程度 | ⭐⭐⭐⭐ |
| 枚举值 | 0 (有货), 1 (缺货) |

**含义**: 当日是否处于缺货状态。

**为什么重要**: 
- 缺货记录需要特殊处理
- 可选择剔除或插值
- 避免模型学习到错误的需求模式

---

## 重要程度说明

| 等级 | 星级 | 含义 | 对预测的影响 |
|------|------|------|--------------|
| 必需 | ⭐⭐⭐⭐⭐ | 缺少则预测严重失准 | 核心输入，必须提供 |
| 强烈建议 | ⭐⭐⭐⭐ | 显著提升准确率 | 可提升10-20%准确率 |
| 建议 | ⭐⭐⭐ | 捕捉特殊事件 | 可提升5-10%准确率 |
| 可选 | ⭐⭐ | 锦上添花 | 边际提升<5% |

---

## 数据预处理建议

### 1. 节假日标注
```python
# 北美节假日日历
holidays_na = {
    'prime_day': ['2025-07-15', '2025-07-16'],
    'black_friday': ['2025-11-28'],
    'cyber_monday': ['2025-12-01'],
    'thanksgiving': ['2025-11-27'],
    'christmas_season': pd.date_range('2025-11-15', '2025-12-25'),
    # ...
}

# 标注节假日
df['is_prime_day'] = df['date'].isin(holidays_na['prime_day']).astype(int)
df['is_black_friday'] = df['date'].isin(holidays_na['black_friday']).astype(int)
```

### 2. 生命周期计算
```python
df['days_since_launch'] = (df['date'] - df['launch_date']).dt.days

df['product_lifecycle_stage'] = df.apply(
    lambda x: get_lifecycle_stage(x['days_since_launch'], x['has_newer_version']), 
    axis=1
)

df['is_new_product'] = (df['days_since_launch'] <= 90).astype(int)
df['is_declining_product'] = (df['days_since_launch'] > 730).astype(int)
```

### 3. 缺货处理
```python
# 标记缺货
df['is_out_of_stock'] = (df['fba_inventory'] == 0).astype(int)

# 方案1: 剔除缺货记录
df_clean = df[df['is_out_of_stock'] == 0]

# 方案2: 缺货期间销量用前后均值插值
df.loc[df['is_out_of_stock'] == 1, 'sales_quantity'] = None
df['sales_quantity'] = df.groupby('sku')['sales_quantity'].transform(
    lambda x: x.interpolate(method='linear')
)
```

---

## 数据集示例

### 完整推荐数据集

```csv
sku,date,sales_quantity,marketplace,days_since_launch,product_lifecycle_stage,is_prime_day,is_black_friday,is_christmas_season,is_lightning_deal,discount_rate,fba_inventory,is_out_of_stock,ad_spend,bsr_rank
LED-US-0001,2025-07-15,1500,US,450,maturity,1,0,0,1,0.35,2000,0,200,1500
LED-US-0001,2025-07-16,1200,US,451,maturity,1,0,0,0,0.30,800,0,150,1200
LED-US-0001,2025-07-17,180,US,452,maturity,0,0,0,0,0.15,620,0,50,2500
LED-US-0001,2025-11-28,2500,US,586,maturity,0,1,1,1,0.45,3000,0,300,800
```

### 字段说明
- 7月15-16日是Prime Day，销量暴增
- 11月28日是黑五+圣诞季+秒杀，销量最高
- 产品上架450天，处于成熟期
