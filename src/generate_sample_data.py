"""
跨境电商大卖销量预测 - 模拟数据生成器
800个SKU，年销售额约50亿人民币，2024年1月至今
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 1, 30)
NUM_SKUS = 800
TARGET_ANNUAL_REVENUE_USD = 700_000_000  # 约7亿美元/年 ≈ 50亿人民币

# 产品线配置 (智能家居类)
PRODUCT_LINES = {
    "led_strip": {
        "weight": 0.35,  # 占比35%，核心产品
        "base_sales": (50, 180),
        "price_range": (15, 45),
        "q4_boost": 3.5,
        "halloween_boost": 3.0,
    },
    "smart_light": {
        "weight": 0.25,
        "base_sales": (30, 120),
        "price_range": (20, 60),
        "q4_boost": 2.8,
        "halloween_boost": 2.0,
    },
    "tv_backlight": {
        "weight": 0.15,
        "base_sales": (25, 100),
        "price_range": (25, 55),
        "q4_boost": 3.0,
        "halloween_boost": 1.5,
    },
    "outdoor_light": {
        "weight": 0.10,
        "base_sales": (20, 80),
        "price_range": (30, 80),
        "q4_boost": 2.5,
        "halloween_boost": 2.5,
    },
    "smart_sensor": {
        "weight": 0.08,
        "base_sales": (15, 60),
        "price_range": (15, 40),
        "q4_boost": 2.0,
        "halloween_boost": 1.2,
    },
    "accessory": {
        "weight": 0.07,
        "base_sales": (40, 150),
        "price_range": (8, 20),
        "q4_boost": 2.5,
        "halloween_boost": 1.5,
    },
}

# 站点配置
MARKETPLACES = {
    "US": {"weight": 0.55, "currency": "USD"},
    "UK": {"weight": 0.12, "currency": "GBP"},
    "DE": {"weight": 0.15, "currency": "EUR"},
    "FR": {"weight": 0.06, "currency": "EUR"},
    "IT": {"weight": 0.04, "currency": "EUR"},
    "ES": {"weight": 0.04, "currency": "EUR"},
    "CA": {"weight": 0.04, "currency": "CAD"},
}

# 节假日
HOLIDAYS = {
    2024: {
        "prime_day": [datetime(2024, 7, 16), datetime(2024, 7, 17)],
        "prime_day_oct": [datetime(2024, 10, 8), datetime(2024, 10, 9)],
        "halloween": datetime(2024, 10, 31),
        "black_friday": datetime(2024, 11, 29),
        "cyber_monday": datetime(2024, 12, 2),
        "christmas": datetime(2024, 12, 25),
    },
    2025: {
        "prime_day": [datetime(2025, 7, 15), datetime(2025, 7, 16)],
        "prime_day_oct": [datetime(2025, 10, 7), datetime(2025, 10, 8)],
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
    """生成SKU元数据"""
    skus = []
    sku_id = 0
    
    # 按产品线分配SKU数量
    for product_line, config in PRODUCT_LINES.items():
        line_sku_count = int(num_skus * config["weight"])
        
        for i in range(line_sku_count):
            if sku_id >= num_skus:
                break
            
            # 上架日期分布：老品多，新品少
            if sku_id < num_skus * 0.3:
                # 30% 是2024年前的老品
                launch_date = START_DATE - timedelta(days=np.random.randint(180, 720))
            elif sku_id < num_skus * 0.6:
                # 30% 是2024年上架
                launch_date = START_DATE + timedelta(days=np.random.randint(0, 365))
            else:
                # 40% 是2025年上架的新品
                launch_date = datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 395))
            
            launch_date = min(launch_date, END_DATE - timedelta(days=30))
            
            # 生命周期
            lifecycle_months = np.random.randint(12, 30)
            
            # 是否下架
            potential_end = launch_date + timedelta(days=lifecycle_months * 30)
            is_active = potential_end > END_DATE or np.random.random() > 0.15
            end_date = None if is_active else potential_end
            
            # 站点分布
            marketplace = random.choices(
                list(MARKETPLACES.keys()),
                weights=[m["weight"] for m in MARKETPLACES.values()]
            )[0]
            
            # 价格
            base_price = round(np.random.uniform(*config["price_range"]), 2)
            
            # 基础销量 (头部产品销量更高)
            if i < line_sku_count * 0.1:  # Top 10%
                base_sales = int(np.random.uniform(config["base_sales"][1] * 1.5, config["base_sales"][1] * 3))
            elif i < line_sku_count * 0.3:  # Top 30%
                base_sales = int(np.random.uniform(*config["base_sales"]))
            else:  # 长尾
                base_sales = int(np.random.uniform(config["base_sales"][0] * 0.3, config["base_sales"][0]))
            
            skus.append({
                "asin": f"B0{sku_id:07d}",
                "sku": f"{product_line[:3].upper()}-{marketplace}-{sku_id:04d}",
                "product_line": product_line,
                "marketplace": marketplace,
                "launch_date": launch_date,
                "end_date": end_date,
                "is_active": is_active,
                "base_sales": base_sales,
                "base_price": base_price,
                "lifecycle_months": lifecycle_months,
            })
            sku_id += 1
    
    # 补齐剩余SKU
    while sku_id < num_skus:
        product_line = random.choice(list(PRODUCT_LINES.keys()))
        config = PRODUCT_LINES[product_line]
        marketplace = random.choices(
            list(MARKETPLACES.keys()),
            weights=[m["weight"] for m in MARKETPLACES.values()]
        )[0]
        
        launch_date = datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 395))
        launch_date = min(launch_date, END_DATE - timedelta(days=30))
        
        skus.append({
            "asin": f"B0{sku_id:07d}",
            "sku": f"{product_line[:3].upper()}-{marketplace}-{sku_id:04d}",
            "product_line": product_line,
            "marketplace": marketplace,
            "launch_date": launch_date,
            "end_date": None,
            "is_active": True,
            "base_sales": int(np.random.uniform(config["base_sales"][0] * 0.3, config["base_sales"][0])),
            "base_price": round(np.random.uniform(*config["price_range"]), 2),
            "lifecycle_months": np.random.randint(12, 24),
        })
        sku_id += 1
    
    return pd.DataFrame(skus)


def get_seasonal_factor(date: datetime, product_line: str) -> float:
    """季节性因子"""
    config = PRODUCT_LINES[product_line]
    month = date.month
    
    if month in [11, 12]:
        return config["q4_boost"]
    if month == 10:
        return config["halloween_boost"]
    if month in [8, 9]:
        return 1.25
    if month == 7:
        return 1.35
    if month in [1, 2]:
        return 0.65
    if month == 3:
        return 0.75
    return 1.0


def get_holiday_factor(date: datetime, marketplace: str) -> float:
    """节假日因子"""
    year = date.year
    if year not in HOLIDAYS:
        return 1.0
    
    holidays = HOLIDAYS[year]
    
    # Prime Day
    for key in ["prime_day", "prime_day_oct"]:
        if key in holidays:
            for pd_date in holidays[key]:
                if date == pd_date:
                    return 6.0 if marketplace == "US" else 4.0
                if 0 < (pd_date - date).days <= 5:
                    return 1.8
    
    # 黑五
    if "black_friday" in holidays:
        bf = holidays["black_friday"]
        if date == bf:
            return 10.0
        days_diff = (bf - date).days
        if 0 < days_diff <= 3:
            return 4.0
        if 3 < days_diff <= 7:
            return 2.5
    
    # 网一
    if "cyber_monday" in holidays:
        cm = holidays["cyber_monday"]
        if date == cm:
            return 7.0
    
    # 圣诞前
    if "christmas" in holidays:
        xmas = holidays["christmas"]
        days_to_xmas = (xmas - date).days
        if 0 < days_to_xmas <= 5:
            return 3.0
        if 5 < days_to_xmas <= 14:
            return 2.2
    
    # 万圣节
    if "halloween" in holidays:
        hw = holidays["halloween"]
        days_to_hw = (hw - date).days
        if 0 <= days_to_hw <= 2:
            return 2.5
        if 2 < days_to_hw <= 7:
            return 1.8
    
    return 1.0


def get_lifecycle_factor(days_since_launch: int, lifecycle_months: int) -> float:
    """生命周期因子"""
    if days_since_launch < 0:
        return 0
    
    total_days = lifecycle_months * 30
    progress = min(days_since_launch / total_days, 1.5)
    
    if progress < 0.05:
        return 0.2 + progress * 10
    elif progress < 0.15:
        return 0.7 + (progress - 0.05) * 4
    elif progress < 0.5:
        return 1.1 + (progress - 0.15) * 0.5
    elif progress < 0.8:
        return 1.3
    else:
        return max(0.3, 1.3 - (progress - 0.8) * 2)


def generate_daily_sales(sku_meta: pd.DataFrame) -> pd.DataFrame:
    """生成每日销量数据"""
    all_data = []
    
    for _, sku in sku_meta.iterrows():
        launch = sku["launch_date"]
        end = sku["end_date"] if pd.notna(sku["end_date"]) else END_DATE
        
        # 只生成2024年1月1日之后的数据
        start = max(launch, START_DATE)
        if start >= end:
            continue
        
        dates = pd.date_range(start, min(end, END_DATE), freq="D")
        
        for date in dates:
            days_since_launch = (date - launch).days
            
            base = sku["base_sales"]
            seasonal = get_seasonal_factor(date, sku["product_line"])
            holiday = get_holiday_factor(date, sku["marketplace"])
            lifecycle = get_lifecycle_factor(days_since_launch, sku["lifecycle_months"])
            weekend = 1.12 if date.dayofweek >= 5 else 1.0
            noise = np.random.uniform(0.75, 1.25)
            
            sales = int(base * seasonal * holiday * lifecycle * weekend * noise)
            sales = max(0, sales)
            
            # 价格
            base_price = sku["base_price"]
            discount = 0
            if holiday > 3:
                discount = np.random.uniform(0.2, 0.4)
            elif holiday > 1.5:
                discount = np.random.uniform(0.1, 0.25)
            elif np.random.random() < 0.08:
                discount = np.random.uniform(0.05, 0.15)
            
            sale_price = round(base_price * (1 - discount), 2)
            
            # 广告
            ad_spend = 0
            ad_impressions = 0
            ad_clicks = 0
            
            if np.random.random() < 0.75:
                ad_base = base * 0.8
                ad_multiplier = seasonal * (1 + (holiday - 1) * 0.5)
                ad_spend = round(np.random.uniform(ad_base * 0.3, ad_base * 1.2) * ad_multiplier, 2)
                ad_impressions = int(ad_spend * np.random.uniform(100, 180))
                ad_clicks = int(ad_impressions * np.random.uniform(0.015, 0.045))
            
            # 库存
            inventory = np.random.randint(300, 3000)
            if np.random.random() < 0.03:
                inventory = np.random.randint(20, 150)
            if np.random.random() < 0.005:
                inventory = 0
                sales = int(sales * 0.1)
            
            # 促销
            is_lightning_deal = 1 if (holiday > 4 and np.random.random() < 0.4) else 0
            is_coupon = 1 if discount > 0.08 else 0
            is_deal_of_day = 1 if (holiday > 6 and np.random.random() < 0.2) else 0
            
            # BSR排名 (销量越高排名越靠前)
            bsr_base = max(1, int(50000 / (sales + 1)))
            bsr_rank = int(bsr_base * np.random.uniform(0.5, 1.5))
            
            # 评分和评论
            rating = round(np.random.uniform(4.0, 4.8), 1)
            review_count = int(days_since_launch * np.random.uniform(0.5, 2.0))
            
            all_data.append({
                "asin": sku["asin"],
                "sku": sku["sku"],
                "marketplace": sku["marketplace"],
                "date": date,
                "sales_quantity": sales,
                "sale_price": sale_price,
                "original_price": base_price,
                "discount_rate": round(discount, 3),
                "ad_spend": ad_spend,
                "ad_impressions": ad_impressions,
                "ad_clicks": ad_clicks,
                "fba_inventory": inventory,
                "is_lightning_deal": is_lightning_deal,
                "is_coupon_active": is_coupon,
                "is_deal_of_day": is_deal_of_day,
                "bsr_rank": bsr_rank,
                "rating": rating,
                "review_count": review_count,
                "product_line": sku["product_line"],
                "launch_date": launch,
            })
    
    return pd.DataFrame(all_data)


def main():
    print("=" * 60)
    print("跨境电商大卖销量数据生成")
    print("=" * 60)
    
    print("\n生成SKU元数据...")
    sku_meta = generate_sku_metadata(NUM_SKUS)
    print(f"  总SKU数: {len(sku_meta)}")
    print(f"  活跃SKU: {sku_meta['is_active'].sum()}")
    print(f"  已下架: {(~sku_meta['is_active']).sum()}")
    
    print("\n产品线分布:")
    print(sku_meta["product_line"].value_counts().to_string())
    
    print("\n站点分布:")
    print(sku_meta["marketplace"].value_counts().to_string())
    
    print("\n生成每日销量数据...")
    sales_df = generate_daily_sales(sku_meta)
    print(f"  总记录数: {len(sales_df):,}")
    print(f"  日期范围: {sales_df['date'].min().date()} ~ {sales_df['date'].max().date()}")
    
    # 计算年销售额
    sales_df["revenue"] = sales_df["sales_quantity"] * sales_df["sale_price"]
    annual_revenue = sales_df.groupby(sales_df["date"].dt.year)["revenue"].sum()
    print("\n年销售额 (USD):")
    for year, rev in annual_revenue.items():
        print(f"  {year}: ${rev:,.0f} (约 {rev * 7.2 / 1e8:.1f} 亿人民币)")
    
    # 保存
    sku_meta.to_csv("data/sku_metadata.csv", index=False)
    sales_df.drop(columns=["revenue"]).to_csv("data/sales_history.csv", index=False)
    
    print("\n" + "=" * 60)
    print("数据已保存到 data/ 目录")
    print(f"  - sku_metadata.csv: {len(sku_meta)} 行")
    print(f"  - sales_history.csv: {len(sales_df):,} 行")
    print("=" * 60)
    
    # 月度趋势
    print("\n月度销量趋势 (最近12个月):")
    monthly = sales_df.groupby(sales_df["date"].dt.to_period("M"))["sales_quantity"].sum()
    print(monthly.tail(12).to_string())


if __name__ == "__main__":
    main()
