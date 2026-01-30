"""
跨境电商销量预测 - 数据预处理与特征工程
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 北美节假日配置
US_HOLIDAYS = {
    "new_year": {"month": 1, "day": 1},
    "super_bowl": {"month": 2, "day": 12},
    "valentines": {"month": 2, "day": 14},
    "memorial_day": {"month": 5, "day": 27},
    "july_4th": {"month": 7, "day": 4},
    "labor_day": {"month": 9, "day": 2},
    "halloween": {"month": 10, "day": 31},
    "thanksgiving": {"month": 11, "day": 28},
    "black_friday": {"month": 11, "day": 29},
    "cyber_monday": {"month": 12, "day": 2},
    "christmas": {"month": 12, "day": 25},
}

# 欧洲节假日配置
EU_HOLIDAYS = {
    "new_year": {"month": 1, "day": 1},
    "carnival": {"month": 2, "day": 20},
    "easter": {"month": 4, "day": 9},
    "boxing_day": {"month": 12, "day": 26},
    "christmas": {"month": 12, "day": 25},
    "black_friday": {"month": 11, "day": 29},
    "singles_day": {"month": 11, "day": 11},
}

# Prime Day 日期
PRIME_DAY_DATES = {
    2023: [datetime(2023, 7, 11), datetime(2023, 7, 12)],
    2024: [datetime(2024, 7, 16), datetime(2024, 7, 17)],
    2025: [datetime(2025, 7, 15), datetime(2025, 7, 16)],
    2026: [datetime(2026, 7, 14), datetime(2026, 7, 15)],
}


def add_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """添加基础时间特征"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    df["day_of_week"] = df[date_col].dt.dayofweek
    df["day_of_month"] = df[date_col].dt.day
    df["month"] = df[date_col].dt.month
    df["quarter"] = df[date_col].dt.quarter
    df["week_of_year"] = df[date_col].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_month_start"] = (df["day_of_month"] <= 3).astype(int)
    df["is_month_end"] = (df["day_of_month"] >= 28).astype(int)
    
    df["season"] = df["month"].map({
        12: "winter", 1: "winter", 2: "winter",
        3: "spring", 4: "spring", 5: "spring",
        6: "summer", 7: "summer", 8: "summer",
        9: "fall", 10: "fall", 11: "fall"
    })
    df["is_winter"] = (df["season"] == "winter").astype(int)
    
    return df


def add_holiday_features(df: pd.DataFrame, marketplace: str, date_col: str = "date") -> pd.DataFrame:
    """添加节假日特征"""
    df = df.copy()
    holidays = US_HOLIDAYS if marketplace in ["US", "CA"] else EU_HOLIDAYS
    
    for name, info in holidays.items():
        df[f"is_{name}"] = ((df[date_col].dt.month == info["month"]) & 
                           (df[date_col].dt.day == info["day"])).astype(int)
    
    # 万圣节季 (10月)
    df["is_halloween_season"] = (df[date_col].dt.month == 10).astype(int)
    
    # 圣诞季 (11月15日-12月25日)
    df["is_christmas_season"] = (
        ((df[date_col].dt.month == 11) & (df[date_col].dt.day >= 15)) |
        ((df[date_col].dt.month == 12) & (df[date_col].dt.day <= 25))
    ).astype(int)
    
    # 黑五周
    df["is_black_friday_week"] = (
        (df[date_col].dt.month == 11) & (df[date_col].dt.day >= 24)
    ).astype(int)
    
    # 返校季 (8月-9月中旬)
    df["is_back_to_school"] = (
        (df[date_col].dt.month == 8) |
        ((df[date_col].dt.month == 9) & (df[date_col].dt.day <= 15))
    ).astype(int)
    
    # Prime Day
    df["is_prime_day"] = 0
    for year, dates in PRIME_DAY_DATES.items():
        for d in dates:
            df.loc[df[date_col] == d, "is_prime_day"] = 1
    
    # Prime Day 预热期
    df["is_prime_day_warmup"] = 0
    for year, dates in PRIME_DAY_DATES.items():
        start = dates[0] - timedelta(days=7)
        end = dates[0] - timedelta(days=1)
        df.loc[(df[date_col] >= start) & (df[date_col] <= end), "is_prime_day_warmup"] = 1
    
    # 距离最近重要节日天数
    df["days_to_major_holiday"] = _calc_days_to_holiday(df, date_col, marketplace)
    
    return df


def _calc_days_to_holiday(df: pd.DataFrame, date_col: str, marketplace: str) -> pd.Series:
    """计算距离最近重要节日的天数"""
    major_holidays = ["halloween", "black_friday", "christmas"]
    
    def get_days(row):
        year = row[date_col].year
        min_days = 365
        for h in major_holidays:
            info = US_HOLIDAYS.get(h, EU_HOLIDAYS.get(h))
            if info:
                h_date = datetime(year, info["month"], info["day"])
                if h_date < row[date_col]:
                    h_date = datetime(year + 1, info["month"], info["day"])
                days = (h_date - row[date_col]).days
                min_days = min(min_days, days)
        return min_days
    
    return df.apply(get_days, axis=1)


def add_promotion_features(df: pd.DataFrame) -> pd.DataFrame:
    """添加促销特征"""
    df = df.copy()
    
    if "original_price" in df.columns and "sale_price" in df.columns:
        df["discount_rate"] = 1 - df["sale_price"] / df["original_price"]
        df["discount_rate"] = df["discount_rate"].clip(0, 1).fillna(0)
    
    promo_cols = ["is_lightning_deal", "is_coupon_active", "is_deal_of_day"]
    for col in promo_cols:
        if col not in df.columns:
            df[col] = 0
    
    df["has_promotion"] = (
        df["is_lightning_deal"] | df["is_coupon_active"] | df["is_deal_of_day"]
    ).astype(int)
    
    return df


def add_product_lifecycle_features(df: pd.DataFrame, launch_date_col: str = "launch_date", 
                                   date_col: str = "date") -> pd.DataFrame:
    """添加产品生命周期特征"""
    df = df.copy()
    
    if launch_date_col in df.columns:
        df[launch_date_col] = pd.to_datetime(df[launch_date_col])
        df["days_since_launch"] = (df[date_col] - df[launch_date_col]).dt.days
        
        df["lifecycle_stage"] = pd.cut(
            df["days_since_launch"],
            bins=[-1, 60, 180, 365, float("inf")],
            labels=["new", "growth", "mature", "legacy"]
        )
        df["is_new_product"] = (df["days_since_launch"] <= 60).astype(int)
    
    return df


def add_advertising_features(df: pd.DataFrame) -> pd.DataFrame:
    """添加广告特征"""
    df = df.copy()
    
    ad_cols = ["ad_spend", "ad_impressions", "ad_clicks"]
    for col in ad_cols:
        if col not in df.columns:
            df[col] = 0
    
    df["ad_ctr"] = np.where(df["ad_impressions"] > 0, 
                           df["ad_clicks"] / df["ad_impressions"], 0)
    df["ad_cpc"] = np.where(df["ad_clicks"] > 0,
                           df["ad_spend"] / df["ad_clicks"], 0)
    df["has_advertising"] = (df["ad_spend"] > 0).astype(int)
    
    return df


def add_inventory_features(df: pd.DataFrame) -> pd.DataFrame:
    """添加库存特征"""
    df = df.copy()
    
    if "fba_inventory" in df.columns:
        df["is_low_stock"] = (df["fba_inventory"] < 100).astype(int)
        df["is_out_of_stock"] = (df["fba_inventory"] == 0).astype(int)
    
    return df


def add_lag_features(df: pd.DataFrame, target_col: str = "sales_quantity",
                     group_col: str = "asin", lags: list = [7, 14, 28]) -> pd.DataFrame:
    """添加滞后特征"""
    df = df.sort_values([group_col, "date"]).copy()
    
    for lag in lags:
        df[f"sales_lag_{lag}d"] = df.groupby(group_col)[target_col].shift(lag)
    
    for window in [7, 14]:
        df[f"sales_ma_{window}d"] = df.groupby(group_col)[target_col].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).mean()
        )
        df[f"sales_std_{window}d"] = df.groupby(group_col)[target_col].transform(
            lambda x: x.shift(1).rolling(window, min_periods=1).std()
        )
    
    return df


def preprocess_data(df: pd.DataFrame, marketplace: str = "US") -> pd.DataFrame:
    """主预处理函数"""
    df = df.copy()
    df = add_time_features(df)
    df = add_holiday_features(df, marketplace)
    df = add_promotion_features(df)
    df = add_product_lifecycle_features(df)
    df = add_advertising_features(df)
    df = add_inventory_features(df)
    df = add_lag_features(df)
    return df


# 协变量字段定义
PAST_COVARIATES = [
    "day_of_week", "month", "is_weekend",
    "is_halloween_season", "is_christmas_season", "is_black_friday_week",
    "is_prime_day", "is_back_to_school", "days_to_major_holiday",
    "discount_rate", "has_promotion",
    "ad_spend", "has_advertising",
    "is_low_stock", "is_out_of_stock",
    "is_new_product",
]

FUTURE_COVARIATES = [
    "day_of_week", "month", "is_weekend",
    "is_halloween_season", "is_christmas_season", "is_black_friday_week",
    "is_prime_day", "is_back_to_school", "days_to_major_holiday",
]
