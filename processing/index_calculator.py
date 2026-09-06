import pandas as pd
from config.settings import ROUTE_WEIGHTS

def compute_apix_index(df_cleaned: pd.DataFrame, base_prices_map: dict) -> pd.DataFrame:
    """
    Applies the mathematical Laspeyres price formula weighting route relatives 
    according to active DGCA passenger market volumes.
    """
    # 1. Compute daily route means
    daily_routes = df_cleaned.groupby(['flight_date', 'route'])['total_fare'].mean().reset_index()
    
    # 2. Get relative index comparison (R_it = P_it / P_i0 * 100)
    daily_routes['base_price'] = daily_routes['route'].map(base_prices_map)
    daily_routes['price_relative'] = (daily_routes['total_fare'] / daily_routes['base_price']) * 100
    
    # 3. Apply DGCA corridor travel distribution weights
    daily_routes['weight'] = daily_routes['route'].map(ROUTE_WEIGHTS)
    daily_routes['weighted_relative'] = daily_routes['price_relative'] * daily_routes['weight']
    
    # 4. Sum up daily index averages
    apix_daily = daily_routes.groupby('flight_date').apply(
        lambda x: x['weighted_relative'].sum() / x['weight'].sum()
    ).reset_index(name='APIx')
    
    # 5. Formulate rolling 7-day moving baseline
    apix_daily['Weekly_APIx'] = apix_daily['APIx'].rolling(window=7, min_periods=1).mean()
    return apix_daily
