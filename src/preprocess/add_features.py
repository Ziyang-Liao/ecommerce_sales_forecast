"""
添加节假日、生命周期等特征维度
包含完整的美国节假日和Amazon促销日历
"""
import pandas as pd
import numpy as np

def get_us_holidays_and_promotions(year):
    """
    获取美国重要节假日和Amazon促销日历
    包含节日前后的影响期
    """
    holidays = {}
    
    # ========== Amazon 大促 ==========
    # Prime Day (7月中旬，通常2天，但影响期约1周)
    holidays['prime_day'] = pd.date_range(f'{year}-07-15', f'{year}-07-17').strftime('%Y-%m-%d').tolist()
    holidays['prime_day_week'] = pd.date_range(f'{year}-07-12', f'{year}-07-20').strftime('%Y-%m-%d').tolist()
    
    # Prime Big Deal Days (10月，第二个Prime Day)
    holidays['prime_big_deal_days'] = pd.date_range(f'{year}-10-10', f'{year}-10-12').strftime('%Y-%m-%d').tolist()
    
    # ========== 感恩节 & 黑五周 ==========
    # 计算感恩节 (11月第4个周四)
    nov1 = pd.Timestamp(f'{year}-11-01')
    days_until_thu = (3 - nov1.dayofweek + 7) % 7
    first_thu = nov1 + pd.Timedelta(days=days_until_thu)
    thanksgiving = first_thu + pd.Timedelta(weeks=3)
    
    holidays['thanksgiving'] = [thanksgiving.strftime('%Y-%m-%d')]
    
    # 黑色星期五 (感恩节后一天)
    black_friday = thanksgiving + pd.Timedelta(days=1)
    holidays['black_friday'] = [black_friday.strftime('%Y-%m-%d')]
    
    # 黑五周 (感恩节前一周到网一后)
    bf_week_start = thanksgiving - pd.Timedelta(days=7)
    bf_week_end = thanksgiving + pd.Timedelta(days=5)
    holidays['black_friday_week'] = pd.date_range(bf_week_start, bf_week_end).strftime('%Y-%m-%d').tolist()
    
    # 网络星期一 (感恩节后的周一)
    cyber_monday = thanksgiving + pd.Timedelta(days=4)
    holidays['cyber_monday'] = [cyber_monday.strftime('%Y-%m-%d')]
    
    # Cyber Week (网一后一周)
    holidays['cyber_week'] = pd.date_range(cyber_monday, cyber_monday + pd.Timedelta(days=6)).strftime('%Y-%m-%d').tolist()
    
    # ========== 圣诞季 ==========
    # 圣诞季 (11.15 - 12.25)
    holidays['christmas_season'] = pd.date_range(f'{year}-11-15', f'{year}-12-25').strftime('%Y-%m-%d').tolist()
    
    # 圣诞节
    holidays['christmas'] = [f'{year}-12-25']
    
    # 圣诞前最后冲刺 (12.15-12.24)
    holidays['christmas_rush'] = pd.date_range(f'{year}-12-15', f'{year}-12-24').strftime('%Y-%m-%d').tolist()
    
    # Boxing Day / 节后促销 (12.26 - 12.31)
    holidays['post_christmas'] = pd.date_range(f'{year}-12-26', f'{year}-12-31').strftime('%Y-%m-%d').tolist()
    
    # ========== 万圣节 ==========
    holidays['halloween'] = [f'{year}-10-31']
    holidays['halloween_season'] = pd.date_range(f'{year}-10-01', f'{year}-10-31').strftime('%Y-%m-%d').tolist()
    
    # ========== 返校季 ==========
    holidays['back_to_school'] = pd.date_range(f'{year}-07-15', f'{year}-09-15').strftime('%Y-%m-%d').tolist()
    
    # ========== 情人节 ==========
    holidays['valentines_day'] = [f'{year}-02-14']
    holidays['valentines_week'] = pd.date_range(f'{year}-02-07', f'{year}-02-14').strftime('%Y-%m-%d').tolist()
    
    # ========== 母亲节 (5月第2个周日) ==========
    may1 = pd.Timestamp(f'{year}-05-01')
    days_until_sun = (6 - may1.dayofweek + 7) % 7
    first_sun = may1 + pd.Timedelta(days=days_until_sun)
    mothers_day = first_sun + pd.Timedelta(weeks=1)
    holidays['mothers_day'] = [mothers_day.strftime('%Y-%m-%d')]
    holidays['mothers_day_week'] = pd.date_range(mothers_day - pd.Timedelta(days=7), mothers_day).strftime('%Y-%m-%d').tolist()
    
    # ========== 父亲节 (6月第3个周日) ==========
    jun1 = pd.Timestamp(f'{year}-06-01')
    days_until_sun = (6 - jun1.dayofweek + 7) % 7
    first_sun = jun1 + pd.Timedelta(days=days_until_sun)
    fathers_day = first_sun + pd.Timedelta(weeks=2)
    holidays['fathers_day'] = [fathers_day.strftime('%Y-%m-%d')]
    holidays['fathers_day_week'] = pd.date_range(fathers_day - pd.Timedelta(days=7), fathers_day).strftime('%Y-%m-%d').tolist()
    
    # ========== 劳动节 (9月第1个周一) ==========
    sep1 = pd.Timestamp(f'{year}-09-01')
    days_until_mon = (0 - sep1.dayofweek + 7) % 7
    labor_day = sep1 + pd.Timedelta(days=days_until_mon)
    holidays['labor_day'] = [labor_day.strftime('%Y-%m-%d')]
    holidays['labor_day_weekend'] = pd.date_range(labor_day - pd.Timedelta(days=2), labor_day).strftime('%Y-%m-%d').tolist()
    
    # ========== 阵亡将士纪念日 (5月最后一个周一) ==========
    may31 = pd.Timestamp(f'{year}-05-31')
    days_back_to_mon = (may31.dayofweek - 0 + 7) % 7
    memorial_day = may31 - pd.Timedelta(days=days_back_to_mon)
    holidays['memorial_day'] = [memorial_day.strftime('%Y-%m-%d')]
    holidays['memorial_day_weekend'] = pd.date_range(memorial_day - pd.Timedelta(days=2), memorial_day).strftime('%Y-%m-%d').tolist()
    
    # ========== 独立日 (7月4日) ==========
    holidays['independence_day'] = [f'{year}-07-04']
    holidays['independence_day_week'] = pd.date_range(f'{year}-07-01', f'{year}-07-07').strftime('%Y-%m-%d').tolist()
    
    # ========== 新年 ==========
    holidays['new_year'] = [f'{year}-01-01']
    holidays['new_year_week'] = pd.date_range(f'{year}-01-01', f'{year}-01-07').strftime('%Y-%m-%d').tolist()
    
    # ========== 复活节 (春分后第一个满月后的周日，简化处理) ==========
    # 2024: 3/31, 2025: 4/20, 2026: 4/5
    easter_dates = {2024: '2024-03-31', 2025: '2025-04-20', 2026: '2026-04-05'}
    if year in easter_dates:
        easter = pd.Timestamp(easter_dates[year])
        holidays['easter'] = [easter.strftime('%Y-%m-%d')]
        holidays['easter_week'] = pd.date_range(easter - pd.Timedelta(days=7), easter).strftime('%Y-%m-%d').tolist()
    
    # ========== Super Bowl (2月第2个周日) ==========
    feb1 = pd.Timestamp(f'{year}-02-01')
    days_until_sun = (6 - feb1.dayofweek + 7) % 7
    first_sun = feb1 + pd.Timedelta(days=days_until_sun)
    super_bowl = first_sun + pd.Timedelta(weeks=1)
    holidays['super_bowl'] = [super_bowl.strftime('%Y-%m-%d')]
    holidays['super_bowl_week'] = pd.date_range(super_bowl - pd.Timedelta(days=7), super_bowl).strftime('%Y-%m-%d').tolist()
    
    return holidays

def add_holiday_features(df):
    """添加节假日特征"""
    df = df.copy()
    
    # 获取所有年份的节假日
    years = df['date'].dt.year.unique()
    
    # 初始化所有节假日字典
    holiday_keys = [
        'prime_day', 'prime_day_week', 'prime_big_deal_days',
        'thanksgiving', 'black_friday', 'black_friday_week', 'cyber_monday', 'cyber_week',
        'christmas_season', 'christmas', 'christmas_rush', 'post_christmas',
        'halloween', 'halloween_season',
        'back_to_school',
        'valentines_day', 'valentines_week',
        'mothers_day', 'mothers_day_week',
        'fathers_day', 'fathers_day_week',
        'labor_day', 'labor_day_weekend',
        'memorial_day', 'memorial_day_weekend',
        'independence_day', 'independence_day_week',
        'new_year', 'new_year_week',
        'easter', 'easter_week',
        'super_bowl', 'super_bowl_week'
    ]
    
    all_holidays = {k: [] for k in holiday_keys}
    
    for year in years:
        holidays = get_us_holidays_and_promotions(year)
        for key in holiday_keys:
            if key in holidays:
                all_holidays[key].extend(holidays[key])
    
    # 添加节假日标记
    date_str = df['date'].dt.strftime('%Y-%m-%d')
    
    # Amazon 大促
    df['is_prime_day'] = date_str.isin(all_holidays['prime_day']).astype(int)
    df['is_prime_day_week'] = date_str.isin(all_holidays['prime_day_week']).astype(int)
    df['is_prime_big_deal_days'] = date_str.isin(all_holidays['prime_big_deal_days']).astype(int)
    
    # 黑五周
    df['is_thanksgiving'] = date_str.isin(all_holidays['thanksgiving']).astype(int)
    df['is_black_friday'] = date_str.isin(all_holidays['black_friday']).astype(int)
    df['is_black_friday_week'] = date_str.isin(all_holidays['black_friday_week']).astype(int)
    df['is_cyber_monday'] = date_str.isin(all_holidays['cyber_monday']).astype(int)
    df['is_cyber_week'] = date_str.isin(all_holidays['cyber_week']).astype(int)
    
    # 圣诞季
    df['is_christmas_season'] = date_str.isin(all_holidays['christmas_season']).astype(int)
    df['is_christmas'] = date_str.isin(all_holidays['christmas']).astype(int)
    df['is_christmas_rush'] = date_str.isin(all_holidays['christmas_rush']).astype(int)
    df['is_post_christmas'] = date_str.isin(all_holidays['post_christmas']).astype(int)
    
    # 万圣节
    df['is_halloween'] = date_str.isin(all_holidays['halloween']).astype(int)
    df['is_halloween_season'] = date_str.isin(all_holidays['halloween_season']).astype(int)
    
    # 其他节日
    df['is_back_to_school'] = date_str.isin(all_holidays['back_to_school']).astype(int)
    df['is_valentines_week'] = date_str.isin(all_holidays['valentines_week']).astype(int)
    df['is_mothers_day_week'] = date_str.isin(all_holidays['mothers_day_week']).astype(int)
    df['is_fathers_day_week'] = date_str.isin(all_holidays['fathers_day_week']).astype(int)
    df['is_labor_day_weekend'] = date_str.isin(all_holidays['labor_day_weekend']).astype(int)
    df['is_memorial_day_weekend'] = date_str.isin(all_holidays['memorial_day_weekend']).astype(int)
    df['is_independence_day_week'] = date_str.isin(all_holidays['independence_day_week']).astype(int)
    df['is_new_year_week'] = date_str.isin(all_holidays['new_year_week']).astype(int)
    df['is_easter_week'] = date_str.isin(all_holidays.get('easter_week', [])).astype(int)
    df['is_super_bowl_week'] = date_str.isin(all_holidays['super_bowl_week']).astype(int)
    
    # 综合促销标记
    df['is_major_sale_event'] = (
        df['is_prime_day'] | df['is_black_friday'] | df['is_cyber_monday']
    ).astype(int)
    
    df['is_holiday_season'] = (
        df['is_christmas_season'] | df['is_halloween_season'] | df['is_back_to_school']
    ).astype(int)
    
    # 时间特征
    df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['quarter'] = df['date'].dt.quarter
    
    return df

def add_lifecycle_features(df):
    """添加产品生命周期特征"""
    df = df.copy()
    
    # 上架天数
    df['days_since_launch'] = (df['date'] - df['launch_date']).dt.days
    
    # 生命周期阶段
    conditions = [
        df['days_since_launch'] <= 90,
        df['days_since_launch'] <= 365,
        df['days_since_launch'] <= 730,
        df['days_since_launch'] <= 1095,
    ]
    choices = ['introduction', 'growth', 'maturity', 'decline']
    df['product_lifecycle_stage'] = np.select(conditions, choices, default='end_of_life')
    
    # 阶段编码
    stage_map = {'introduction': 0, 'growth': 1, 'maturity': 2, 'decline': 3, 'end_of_life': 4}
    df['lifecycle_stage_code'] = df['product_lifecycle_stage'].map(stage_map)
    
    df['is_new_product'] = (df['days_since_launch'] <= 90).astype(int)
    df['is_growth_stage'] = ((df['days_since_launch'] > 90) & (df['days_since_launch'] <= 365)).astype(int)
    df['is_mature_product'] = ((df['days_since_launch'] > 365) & (df['days_since_launch'] <= 730)).astype(int)
    df['is_declining'] = (df['days_since_launch'] > 730).astype(int)
    
    return df

def add_inventory_features(df):
    """添加库存特征"""
    df = df.copy()
    df['is_out_of_stock'] = (df['fba_inventory'] == 0).astype(int)
    df['is_low_stock'] = (df['fba_inventory'] < 50).astype(int)
    return df

def add_all_features(input_path, output_path):
    """添加所有特征"""
    print(f"读取: {input_path}")
    df = pd.read_csv(input_path, parse_dates=['date', 'launch_date'])
    
    print(f"日期范围: {df['date'].min().date()} ~ {df['date'].max().date()}")
    print(f"原始字段数: {len(df.columns)}")
    
    df = add_holiday_features(df)
    df = add_lifecycle_features(df)
    df = add_inventory_features(df)
    
    df.to_csv(output_path, index=False)
    print(f"\n保存: {output_path}")
    print(f"新字段数: {len(df.columns)}")
    
    # 验证
    print(f"\n=== 节假日/促销统计 ===")
    print(f"Prime Day: {df['is_prime_day'].sum()} 条")
    print(f"Prime Day周: {df['is_prime_day_week'].sum()} 条")
    print(f"黑色星期五: {df['is_black_friday'].sum()} 条")
    print(f"黑五周: {df['is_black_friday_week'].sum()} 条")
    print(f"网络星期一: {df['is_cyber_monday'].sum()} 条")
    print(f"圣诞季: {df['is_christmas_season'].sum()} 条")
    print(f"万圣节季: {df['is_halloween_season'].sum()} 条")
    print(f"返校季: {df['is_back_to_school'].sum()} 条")
    
    print(f"\n=== 生命周期分布 ===")
    print(df['product_lifecycle_stage'].value_counts())
    
    print(f"\n=== 新增字段列表 ===")
    original_cols = pd.read_csv(input_path, nrows=1).columns.tolist()
    new_cols = [c for c in df.columns if c not in original_cols]
    print(new_cols)
    
    return df

if __name__ == "__main__":
    add_all_features('data/sales_history.csv', 'data/sales_history_enriched.csv')
