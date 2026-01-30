"""
跨境电商销量预测 - 模拟数据生成器
生成100个SKU，2年历史数据，包含产品生命周期、节假日、促销等特征
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 配置
np.random.seed(42)
random.seed(42)

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 1, 30)
NUM_SKUS = 100
MAX_LIFECYCLE_DAYS = 730  # 最长生命周期2年

# 产品类目配置 (不同类目有不同的季节性)
CATEGORIES = {
    "home_decor": {"base_sales": (50, 200), "q4_boost": 3.0, "halloween_boost": 2.5},
    "electronics": {"base_sales": (30, 150), "q4_boost": 2.5, "halloween_boost": 1.2},
    "outdoor": {"base_sales": (40, 180), "q4_boost": 1.5, "halloween_boost": 1.0},
    "toys": {"base_sales": (60, 250), "q4_boost": 4.0, "halloween_boost": 1.5},
    "kitchen": {"base_sales": (35, 120), "q4_boost": 2.0, "halloween_boost": 1.0},
}

# 节假日日期
HOLIDAYS = {
    2024: {
        "prime_day": [datetime(2024, 7, 16), datetime(2024, 7, 17)],
        "halloween": datetime(2024, 10, 31),
        "black_friday": datetime(2024, 11, 29),
        "cyber_monday": datetime(2024, 12, 2),
        "christmas": datetime(2024, 12, 25),
    },
    2025: {
        "prime_day": [datetime(2025, 7, 15), datetime(2025, 7, 16)],
        "halloween": datetime(2025, 10, 31),
        "black_friday": datetime(2025, 11, 28),
        "cyber_monday": datetime(2025, 12, 1),
        "christmas": datetime(2025, 12, 25),
    },
    2026: {
        "prime_day": [datetime(2026, 7, 14), datetime(2026, 7, 15)],
        "halloween": datetime(2026, 10, 31),
        "black_friday": datetime(2026, 11, 27),
        "cyber_monday": datetime(2026, 11, 30),
        "christmas": datetime(2026, 12, 25),
    },
}


def generate_sku_metadata(num_skus: int) -> pd.DataFrame:
    """生成SKU元数据，包含上架日期、类目等"""
    skus = []
    
    # 每月发布新品数量分布
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    
    sku_id = 0
    for month in months:
        # 每月发布3-8个新品
        new_products = np.random.randint(3, 9)
        for _ in range(new_products):
            if sku_id >= num_skus:
                break
            
            # 随机上架日期 (当月内)
            days_in_month = (month + pd.offsets.MonthEnd(0)).day
            launch_day = np.random.randint(1, min(days_in_month, 28) + 1)
            launch_date = month.replace(day=launch_day)
            
            # 生命周期 (6-24个月)
            lifecycle_months = np.random.randint(6, 25)
            end_date = min(launch_date + timedelta(days=lifecycle_months * 30), END_DATE)
            
            # 是否已下架
            is_active = end_date >= END_DATE
            
            category = random.choice(list(CATEGORIES.keys()))
            cat_config = CATEGORIES[category]
            
            skus.append({
                "asin": f"B0{sku_id:07d}",
                "sku": f"SKU-{category[:3].upper()}-{sku_id:04d}",
                "category": category,
                "launch_date": launch_date,
                "end_date": end_date if not is_active else None,
                "is_active": is_active,
                "base_sales": np.random.randint(*cat_config["base_sales"]),
                "base_price": round(np.random.uniform(15, 80), 2),
                "lifecycle_months": lifecycle_months,
            })
            sku_id += 1
        
        if sku_id >= num_skus:
            break
    
    return pd.DataFrame(skus)


def get_seasonal_factor(date: datetime, category: str) -> float:
    """计算季节性因子"""
    cat_config = CATEGORIES[category]
    month = date.month
    
    # Q4 旺季
    if month in [11, 12]:
        return cat_config["q4_boost"]
    # 万圣节季
    if month == 10:
        return cat_config["halloween_boost"]
    # 返校季
    if month in [8, 9]:
        return 1.3
    # Prime Day 月
    if month == 7:
        return 1.4
    # 淡季
    if month in [1, 2, 3]:
        return 0.7
    
    return 1.0


def get_holiday_factor(date: datetime) -> float:
    """计算节假日因子"""
    year = date.year
    if year not in HOLIDAYS:
        return 1.0
    
    holidays = HOLIDAYS[year]
    
    # Prime Day
    if "prime_day" in holidays:
        for pd_date in holidays["prime_day"]:
            if date == pd_date:
                return 5.0
            # 预热期
            if 0 < (pd_date - date).days <= 7:
                return 1.5
    
    # 黑五
    if "black_friday" in holidays:
        bf = holidays["black_friday"]
        if date == bf:
            return 8.0
        # 黑五周
        if 0 <= (bf - date).days <= 3:
            return 3.0
    
    # 网一
    if "cyber_monday" in holidays:
        cm = holidays["cyber_monday"]
        if date == cm:
            return 6.0
    
    # 圣诞前
    if "christmas" in holidays:
        xmas = holidays["christmas"]
        days_to_xmas = (xmas - date).days
        if 0 < days_to_xmas <= 7:
            return 2.5
        if 7 < days_to_xmas <= 14:
            return 2.0
    
    # 万圣节
    if "halloween" in holidays:
        hw = holidays["halloween"]
        days_to_hw = (hw - date).days
        if 0 <= days_to_hw <= 3:
            return 2.0
    
    return 1.0


def get_lifecycle_factor(days_since_launch: int, lifecycle_months: int) -> float:
    """计算产品生命周期因子"""
    total_days = lifecycle_months * 30
    progress = days_since_launch / total_days
    
    # 新品期 (0-10%): 爬坡
    if progress < 0.1:
        return 0.3 + progress * 7
    # 成长期 (10-30%): 快速增长
    elif progress < 0.3:
        return 1.0 + (progress - 0.1) * 2.5
    # 成熟期 (30-70%): 稳定
    elif progress < 0.7:
        return 1.5
    # 衰退期 (70-100%): 下降
    else:
        return 1.5 - (progress - 0.7) * 3
    

def generate_daily_sales(sku_meta: pd.DataFrame) -> pd.DataFrame:
    """生成每日销量数据"""
    all_data = []
    
    for _, sku in sku_meta.iterrows():
        launch = sku["launch_date"]
        end = sku["end_date"] if pd.notna(sku["end_date"]) else END_DATE
        
        dates = pd.date_range(launch, min(end, END_DATE), freq="D")
        
        for date in dates:
            days_since_launch = (date - launch).days
            
            # 基础销量
            base = sku["base_sales"]
            
            # 各种因子
            seasonal = get_seasonal_factor(date, sku["category"])
            holiday = get_holiday_factor(date)
            lifecycle = get_lifecycle_factor(days_since_launch, sku["lifecycle_months"])
            weekend = 1.15 if date.dayofweek >= 5 else 1.0
            
            # 随机波动
            noise = np.random.uniform(0.7, 1.3)
            
            # 最终销量
            sales = int(base * seasonal * holiday * lifecycle * weekend * noise)
            sales = max(0, sales)
            
            # 价格 (促销时打折)
            base_price = sku["base_price"]
            discount = 0
            if holiday > 2:
                discount = np.random.uniform(0.15, 0.35)
            elif np.random.random() < 0.1:  # 10%概率日常促销
                discount = np.random.uniform(0.05, 0.2)
            
            sale_price = round(base_price * (1 - discount), 2)
            
            # 广告数据
            ad_spend = 0
            ad_impressions = 0
            ad_clicks = 0
            
            # 70%的天数有广告投放
            if np.random.random() < 0.7:
                # 旺季广告预算更高
                ad_multiplier = seasonal * holiday
                ad_spend = round(np.random.uniform(20, 100) * ad_multiplier, 2)
                ad_impressions = int(ad_spend * np.random.uniform(80, 150))
                ad_clicks = int(ad_impressions * np.random.uniform(0.01, 0.05))
            
            # 库存
            inventory = np.random.randint(200, 2000)
            # 偶尔低库存
            if np.random.random() < 0.05:
                inventory = np.random.randint(10, 100)
            # 极少断货
            if np.random.random() < 0.01:
                inventory = 0
                sales = 0
            
            # 促销标记
            is_lightning_deal = 1 if (holiday > 3 and np.random.random() < 0.3) else 0
            is_coupon = 1 if discount > 0.1 else 0
            
            all_data.append({
                "asin": sku["asin"],
                "sku": sku["sku"],
                "date": date,
                "sales_quantity": sales,
                "sale_price": sale_price,
                "original_price": base_price,
                "discount_rate": round(discount, 2),
                "ad_spend": ad_spend,
                "ad_impressions": ad_impressions,
                "ad_clicks": ad_clicks,
                "fba_inventory": inventory,
                "is_lightning_deal": is_lightning_deal,
                "is_coupon_active": is_coupon,
                "category": sku["category"],
                "launch_date": launch,
            })
    
    return pd.DataFrame(all_data)


def main():
    print("生成SKU元数据...")
    sku_meta = generate_sku_metadata(NUM_SKUS)
    print(f"生成了 {len(sku_meta)} 个SKU")
    print(f"活跃SKU: {sku_meta['is_active'].sum()}")
    print(f"已下架SKU: {(~sku_meta['is_active']).sum()}")
    
    print("\n生成每日销量数据...")
    sales_df = generate_daily_sales(sku_meta)
    print(f"总记录数: {len(sales_df):,}")
    print(f"日期范围: {sales_df['date'].min()} ~ {sales_df['date'].max()}")
    
    # 保存数据
    sku_meta.to_csv("data/sku_metadata.csv", index=False)
    sales_df.to_csv("data/sales_history.csv", index=False)
    
    print("\n数据已保存到 data/ 目录")
    print(f"  - sku_metadata.csv: {len(sku_meta)} 行")
    print(f"  - sales_history.csv: {len(sales_df):,} 行")
    
    # 统计信息
    print("\n数据统计:")
    print(f"  类目分布:\n{sku_meta['category'].value_counts().to_string()}")
    print(f"\n  月度销量趋势:")
    monthly = sales_df.groupby(sales_df["date"].dt.to_period("M"))["sales_quantity"].sum()
    print(monthly.tail(12).to_string())


if __name__ == "__main__":
    main()
