import pandas as pd
from config.settings import ROUTE_WEIGHTS

def compute_apix_index(df_cleaned: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the mathematical Laspeyres price formula weighting route relatives 
    according to active DGCA passenger market volumes.
    """
    # 1. Establish Base Prices (May 1-3 average)
    df_base_period = df_cleaned[df_cleaned['date'].isin(['2024-05-01', '2024-05-02', '2024-05-03'])]
    base_prices_map = df_base_period.groupby('route')['total_fare'].mean().to_dict()

    # 2. Compute daily route means
    daily_routes = df_cleaned.groupby(['date', 'route'])['total_fare'].mean().reset_index()
    
    # 3. Get relative index comparison (R_it = P_it / P_i0 * 100)
    daily_routes['base_price'] = daily_routes['route'].map(base_prices_map)
    daily_routes['price_relative'] = (daily_routes['total_fare'] / daily_routes['base_price']) * 100
    
    # 4. Apply DGCA corridor travel distribution weights
    daily_routes['weight'] = daily_routes['route'].map(ROUTE_WEIGHTS)
    daily_routes['weighted_relative'] = daily_routes['price_relative'] * daily_routes['weight']
    
    # 5. Sum up daily index averages
    apix_daily = daily_routes.groupby('date').apply(
        lambda x: x['weighted_relative'].sum() / x['weight'].sum()
    ).reset_index(name='APIx')
    
    # 6. Formulate rolling 7-day moving baseline
    apix_daily['Weekly_APIx'] = apix_daily['APIx'].rolling(window=7, min_periods=1).mean()
    return apix_daily
