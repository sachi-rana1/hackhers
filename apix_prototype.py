import numpy as np
import pandas as pd
import datetime
import random

# --- 1. CONFIGURATION & WEIGHTS ---
routes = ['DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU', 'BLR-HYD']
route_weights = {'DEL-BOM': 0.35, 'DEL-BLR': 0.25, 'BOM-BLR': 0.18, 'DEL-CCU': 0.12, 'BLR-HYD': 0.10}
base_prices = {'DEL-BOM': 4500, 'DEL-BLR': 5500, 'BOM-BLR': 4000, 'DEL-CCU': 5000, 'BLR-HYD': 3000}
airlines = ['IndiGo', 'Air India', 'SpiceJet', 'Akasa Air', 'Air India Express']
sources = ['Direct Airline', 'MakeMyTrip', 'EaseMyTrip', 'Yatra', 'Cleartrip', 'ixigo']
lead_times = ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']

# --- 2. ENHANCED SIMULATOR PIPELINE ---
def get_simulated_data(fuel_hike_percent=6.0, holiday_spike_percent=25.0):
    """
    Simulates pricing with dynamic parameter overrides for live 'What-If' simulations.
    """
    np.random.seed(42)
    random.seed(42)
    start_date = datetime.date(2024, 5, 1)
    date_list = [start_date + datetime.timedelta(days=x) for x in range(30)]
    raw_records = []

    # Map multipliers for user parameters
    fuel_multiplier = 1.0 + (fuel_hike_percent / 100.0)
    holiday_multiplier = 1.0 + (holiday_spike_percent / 100.0)

    for d in date_list:
        d_str = d.strftime('%Y-%m-%d')
        # Apply fuel factor post May 13
        current_fuel_factor = fuel_multiplier if d >= datetime.date(2024, 5, 13) else 1.00
        
        for route in routes:
            base_fare_val = base_prices[route]
            # Apply holiday factor post May 20 to May 25
            current_holiday_factor = holiday_multiplier if (route in ['DEL-BOM', 'DEL-BLR'] and datetime.date(2024, 5, 20) <= d <= datetime.date(2024, 5, 25)) else 1.0
                
            for lead in lead_times:
                lead_mult = {'T+1': 2.2, 'T+7': 1.5, 'T+15': 1.1, 'T+30': 1.0, 'T+45': 0.85}[lead]
                for _ in range(5):
                    airline = random.choice(airlines)
                    source = random.choice(sources)
                    
                    base_fare = base_fare_val * lead_mult * current_fuel_factor * current_holiday_factor * np.random.normal(1.0, 0.04)
                    taxes = base_fare * 0.12
                    udf = 500 if 'DEL' in route else 350
                    conv_fee = random.choice([250, 300, 350]) if source != 'Direct Airline' else 0
                    total_fare = base_fare + taxes + udf + conv_fee
                    
                    if random.random() < 0.015: # Random scraper artifacts
                        total_fare = total_fare * random.choice([0.15, 3.5])
                        
                    raw_records.append({
                        'date': d_str, 'route': route, 'airline': airline, 'source': source,
                        'lead_time': lead, 'total_fare': total_fare
                    })
    return pd.DataFrame(raw_records)

def clean_fares(df):
    cleaned_frames = []
    for (route, lead_time), group in df.groupby(['route', 'lead_time']):
        q1, q3 = group['total_fare'].quantile(0.25), group['total_fare'].quantile(0.75)
        iqr = q3 - q1
        cleaned_group = group[(group['total_fare'] >= (q1 - 1.5 * iqr)) & (group['total_fare'] <= (q3 + 1.5 * iqr))]
        cleaned_frames.append(cleaned_group)
    return pd.concat(cleaned_frames).reset_index(drop=True)

# --- 3. ENHANCED MULTI-WINDOW INDEXING ---
def calculate_apix(df_cleaned):
    """
    Computes both the core index and segmented booking-window indexes.
    """
    df_base_period = df_cleaned[df_cleaned['date'].isin(['2024-05-01', '2024-05-02', '2024-05-03'])]
    base_prices_map = df_base_period.groupby('route')['total_fare'].mean().to_dict()
    
    # Helper to calculate index on a subset
    def compute_index(sub_df):
        daily_prices = sub_df.groupby(['date', 'route'])['total_fare'].mean().reset_index()
        daily_prices['base_price'] = daily_prices['route'].map(base_prices_map)
        daily_prices['price_relative'] = (daily_prices['total_fare'] / daily_prices['base_price']) * 100
        daily_prices['weight'] = daily_prices['route'].map(route_weights)
        daily_prices['weighted_relative'] = daily_prices['price_relative'] * daily_prices['weight']
        return daily_prices.groupby('date').apply(lambda x: x['weighted_relative'].sum() / x['weight'].sum()).reset_index()

    # Core Aggregated Index
    apix_overall = compute_index(df_cleaned).rename(columns={0: 'APIx'})
    
    # Segmented T+1 (High-urgency index) & T+45 (Leisure baseline index)
    apix_t1 = compute_index(df_cleaned[df_cleaned['lead_time'] == 'T+1']).rename(columns={0: 'APIx_T1'})
    apix_t45 = compute_index(df_cleaned[df_cleaned['lead_time'] == 'T+45']).rename(columns={0: 'APIx_T45'})
    
    # Merge datasets
    final_df = apix_overall.merge(apix_t1, on='date').merge(apix_t45, on='date')
    final_df['Weekly_APIx'] = final_df['APIx'].rolling(window=7, min_periods=1).mean()
    return final_df

# --- 4. GRAPHRAG EXPLAINER ENGINE ---
knowledge_graph = {
    '2024-05-13': {
        'event': 'ATF Fuel Price Hike', 
        'impact': 'General 5-8% price hike passed onto base fares across India.', 
        'citations': ['MoPNG Circular Ref: 2024-89'],
        'nodes': 'Macroeconomic Cost -> Air Carrier Tariff -> All Routes'
    },
    'holiday_season': {
        'start': '2024-05-20', 'end': '2024-05-25', 
        'event': 'Summer Holiday Demand Peak', 
        'impact': 'Heavy booking spikes (+25%) on DEL-BOM & DEL-BLR.', 
        'citations': ['MMT Summer Travel Trends'],
        'nodes': 'Holiday Calendar -> Traffic Volume -> Metro Corridors'
    }
}

def query_explainer(date_str):
    reasons, citations, nodes = [], [], []
    t_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    if t_date >= datetime.date(2024, 5, 13):
        reasons.append(f"Fuel Hike: {knowledge_graph['2024-05-13']['impact']}")
        citations.extend(knowledge_graph['2024-05-13']['citations'])
        nodes.append(knowledge_graph['2024-05-13']['nodes'])
    if datetime.date(2024, 5, 20) <= t_date <= datetime.date(2024, 5, 25):
        reasons.append(f"Holiday Demand Surge: {knowledge_graph['holiday_season']['impact']}")
        citations.extend(knowledge_graph['holiday_season']['citations'])
        nodes.append(knowledge_graph['holiday_season']['nodes'])
        
    if not reasons:
        return "Normal baseline travel market conditions.", [], "Stability -> Static Baseline"
    return " AND ".join(reasons), list(set(citations)), " | ".join(nodes)

