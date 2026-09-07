import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURATION & WEIGHTS (DGCA BASES)
# ==============================================================================
routes = ['DEL-BOM', 'DEL-BLR', 'BOM-BLR', 'DEL-CCU', 'BLR-HYD']
route_weights = {'DEL-BOM': 0.35, 'DEL-BLR': 0.25, 'BOM-BLR': 0.18, 'DEL-CCU': 0.12, 'BLR-HYD': 0.10}
base_prices = {'DEL-BOM': 4500, 'DEL-BLR': 5500, 'BOM-BLR': 4000, 'DEL-CCU': 5000, 'BLR-HYD': 3000}
airlines = ['IndiGo', 'Air India', 'SpiceJet', 'Akasa Air', 'Air India Express']
sources = ['Direct Airline', 'MakeMyTrip', 'EaseMyTrip', 'Yatra', 'Cleartrip', 'ixigo']
lead_times = ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']

# ==============================================================================
# 2. CORE FUNCTIONS (CLEAN GLOBAL SCOPE - NO NESTING)
# ==============================================================================
def clean_fares(df):
    """
    Cleans raw pricing anomalies using route & lead-time specific IQR bounds.
    """
    cleaned_frames = []
    for (route, lead_time), group in df.groupby(['route', 'lead_time']):
        q1, q3 = group['total_fare'].quantile(0.25), group['total_fare'].quantile(0.75)
        iqr = q3 - q1
        cleaned_group = group[(group['total_fare'] >= (q1 - 1.5 * iqr)) & (group['total_fare'] <= (q3 + 1.5 * iqr))]
        cleaned_frames.append(cleaned_group)
    return pd.concat(cleaned_frames).reset_index(drop=True)

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

    apix_overall = compute_index(df_cleaned).rename(columns={0: 'APIx'})
    apix_t1 = compute_index(df_cleaned[df_cleaned['lead_time'] == 'T+1']).rename(columns={0: 'APIx_T1'})
    apix_t45 = compute_index(df_cleaned[df_cleaned['lead_time'] == 'T+45']).rename(columns={0: 'APIx_T45'})
    
    final_df = apix_overall.merge(apix_t1, on='date').merge(apix_t45, on='date')
    final_df['Weekly_APIx'] = final_df['APIx'].rolling(window=7, min_periods=1).mean()
    return final_df

@st.cache_data
def get_processed_data(fuel_hike_percent=6.0, holiday_spike_percent=25.0):
    """
    Simulates pricing with dynamic parameter overrides for live 'What-If' simulations.
    """
    np.random.seed(42)
    random.seed(42)
    start_date = datetime.date(2024, 5, 1)
    date_list = [start_date + datetime.timedelta(days=x) for x in range(30)]
    raw_records = []
    
    fuel_multiplier = 1.0 + (fuel_hike_percent / 100.0)
    holiday_multiplier = 1.0 + (holiday_spike_percent / 100.0)

    for d in date_list:
        d_str = d.strftime('%Y-%m-%d')
        current_fuel_factor = fuel_multiplier if d >= datetime.date(2024, 5, 13) else 1.00
        
        for route in routes:
            base_fare_val = base_prices[route]
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
                    
                    if random.random() < 0.015:  # Random scraper artifacts
                        total_fare = total_fare * random.choice([0.15, 3.5])
                        
                    raw_records.append({
                        'date': d_str, 'route': route, 'airline': airline, 'source': source,
                        'lead_time': lead, 'total_fare': total_fare
                    })
    df_raw = pd.DataFrame(raw_records)
    df_cleaned = clean_fares(df_raw)
    final_index_df = calculate_apix(df_cleaned)
    return df_raw, df_cleaned, final_index_df

# ==============================================================================
# 3. SEMANTIC GRAPHRAG KNOWLEDGE BASE
# ==============================================================================
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
        reasons.append(f"Holiday Spike: {knowledge_graph['holiday_season']['impact']}")
        citations.extend(knowledge_graph['holiday_season']['citations'])
        nodes.append(knowledge_graph['holiday_season']['nodes'])
        
    if not reasons:
        return "Normal baseline travel market conditions.", [], "Stability -> Static Baseline"
    return " AND ".join(reasons), list(set(citations)), " | ".join(nodes)

# ==============================================================================
# 4. STREAMLIT VISUAL FRONTEND UI
# ==============================================================================
st.set_page_config(page_title="APIx Command Center", page_icon="✈️", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🎛️ Command Controls")
st.sidebar.markdown("### 🔮 'What-If' Market Simulator")
sim_fuel = st.sidebar.slider("ATF Fuel Tariff Hike (%)", min_value=0, max_value=30, value=6, step=1)
sim_holiday = st.sidebar.slider("Seasonal Influx Surge (%)", min_value=0, max_value=100, value=25, step=5)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧮 Data Segment Filter")
selected_airlines = st.sidebar.multiselect("Select Airlines", options=airlines, default=airlines)
selected_channels = st.sidebar.multiselect("Select Channels", options=sources, default=sources)

# Execute core simulation data logic
raw_data, clean_data, apix_df = get_processed_data(sim_fuel, sim_holiday)

# Apply Sidebar filters to raw and clean data
filtered_raw = raw_data[
    (raw_data['airline'].isin(selected_airlines)) & 
    (raw_data['source'].isin(selected_channels))
]

if not filtered_raw.empty:
    filtered_clean = clean_fares(filtered_raw)
    apix_df = calculate_apix(filtered_clean)
else:
    st.warning("No data matches your filter criteria. Please select at least one airline and channel.")
    st.stop()

# --- MAIN PAGE RENDERING ---
st.title("✈️ Real-time Airfare Price Index (APIx) - Command Center")
st.caption("Strategic price tracking prototype incorporating dynamic market simulations — Built for Team HackHers")
st.write("---")

# Metrics row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    latest_idx = apix_df.iloc[-1]['APIx']
    st.metric("Latest Aggregated APIx", f"{latest_idx:.1f}", f"{(latest_idx-100):+.1f}% vs Base")
with kpi2:
    t1_idx = apix_df.iloc[-1]['APIx_T1']
    st.metric("Last-Minute (T+1) Index", f"{t1_idx:.1f}", f"{(t1_idx-100):+.1f}% vs Base")
with kpi3:
    t45_idx = apix_df.iloc[-1]['APIx_T45']
    st.metric("Early-Bird (T+45) Index", f"{t45_idx:.1f}", f"{(t45_idx-100):+.1f}% vs Base")
with kpi4:
    anomalies_removed = len(filtered_raw) - len(filtered_clean)
    st.metric("Outliers Filtered", f"{anomalies_removed}", "Route IQR Bounds")

st.write("---")

# Layout: Main Plot & Explainer
chart_col, explainer_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Multi-Tier Index Analytics")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=apix_df['date'], y=apix_df['APIx'], name="Aggregated APIx", line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=apix_df['date'], y=apix_df['Weekly_APIx'], name="Weekly Trend (7-day MA)", line=dict(color='#ff7f0e', width=2, dash='dash')))
    fig.add_trace(go.Scatter(x=apix_df['date'], y=apix_df['APIx_T1'], name="T+1 High-Urgency", line=dict(color='#d62728', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=apix_df['date'], y=apix_df['APIx_T45'], name="T+45 Leisure Baseline", line=dict(color='#2ca02c', width=1.5, dash='dot')))
    fig.update_layout(xaxis_title="Calculation Date", yaxis_title="Index Level (Base=100)", legend_title="Indices", height=420, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with explainer_col:
    st.subheader("🧠 GraphRAG Explainability")
    test_date = st.selectbox("Select Date to Investigate", apix_df['date'].tolist(), index=21)
    
    explanation, citations, nodes = query_explainer(test_date)
    st.info(f"**AI Explanation:** {explanation}")
    st.markdown(f"**Knowledge Graph Nodes Linked:** `{nodes}`")
    if citations:
        st.warning(f"**Sources cited:** {', '.join(citations)}")

st.write("---")

# Corridor analytics row
col_heat, col_el = st.columns(2)

with col_heat:
    st.subheader("🌡️ Corridor-wise Average Pricing (INR)")
    heat_pivot = filtered_clean.groupby(['route', 'lead_time'])['total_fare'].mean().unstack()[['T+1', 'T+7', 'T+15', 'T+30', 'T+45']]
    fig_heat = px.imshow(heat_pivot, labels=dict(x="Advance Booking Window", y="Route", color="Fare (INR)"), color_continuous_scale="YlOrRd")
    fig_heat.update_layout(height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

with col_el:
    st.subheader("📈 Lead-Time Price Elasticity Curves")
    elast_df = filtered_clean.groupby(['route', 'lead_time'])['total_fare'].mean().reset_index()
    fig_line = px.line(elast_df, x="lead_time", y="total_fare", color="route", markers=True, color_discrete_sequence=px.colors.qualitative.Safe)
    fig_line.update_layout(xaxis_title="Advance Purchase Window", yaxis_title="Average Price (INR)", height=350, margin=dict(t=10, b=10))
    st.plotly_chart(fig_line, use_container_width=True)
