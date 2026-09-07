import streamlit as st
import pandas as pd
import sys
import os

# Dynamic Path Fix: Ensure Python can find parent files
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import apix_prototype as api
from ai_explainability import graph_rag

st.set_page_config(page_title="APIx Command Center", page_icon="✈️", layout="wide")

# --- SIDEBAR: Live Simulator ---
st.sidebar.title("🎛️ Command Controls")
st.sidebar.markdown("### 🔮 'What-If' Market Simulator")
sim_fuel = st.sidebar.slider("ATF Fuel Tariff Hike (%)", min_value=0, max_value=30, value=6, step=1)
sim_holiday = st.sidebar.slider("Seasonal Influx Surge (%)", min_value=0, max_value=100, value=25, step=5)

st.sidebar.markdown("---")
selected_airlines = st.sidebar.multiselect("Select Airlines", options=api.airlines, default=api.airlines)

# --- RUN COMPUTATION ---
raw_data = api.get_simulated_data(sim_fuel, sim_holiday)
filtered_raw = raw_data[raw_data['airline'].isin(selected_airlines)]
clean_data = api.clean_fares(filtered_raw)
apix_df = api.calculate_apix(clean_data)

# --- MAIN PAGE UI ---
st.title("✈️ Real-time Airfare Price Index (APIx) - Dashboard")
st.caption("Modular proof-of-concept analytical framework — Built for Team HackHers")
st.write("---")

col_graph, col_explainer = st.columns()

with col_graph:
    st.subheader("📈 Aggregated Index Trajectory")
    st.line_chart(apix_df.set_index('date')[['APIx', 'Weekly_APIx']])

with col_explainer:
    st.subheader("🧠 GraphRAG Explainability")
    test_date = st.selectbox("Select Date to Investigate", apix_df['date'].tolist(), index=21)
    explanation = graph_rag.explain_price_movement(test_date)
    st.info(f"**AI Explanation:** {explanation['explanation']}")
    st.warning(f"**Categories:** {', '.join(explanation['categories'])}")

st.write("---")

col_heat, col_stats = st.columns(2)
with col_heat:
    st.subheader("🌡️ Average Corridor Fares (INR)")
    heat_df = clean_data.groupby(['route', 'lead_time'])['total_fare'].mean().unstack()[['T+1', 'T+7', 'T+15', 'T+30', 'T+45']]
    st.dataframe(heat_df.style.format("₹{:.0f}"))

with col_stats:
    st.subheader("⚙️ System Status")
    st.success(f"✔️ Dynamic Ingestion Layer: Active")
    st.success(f"✔️ Cleaning Logic (IQR): Removed {len(filtered_raw) - len(clean_data)} price outliers")
import streamlit as st
import pandas as pd
import sys
import os

# Dynamic Path Fix: Ensure Python can find parent files
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import apix_prototype as api
from ai_explainability import graph_rag

st.set_page_config(page_title="APIx Command Center", page_icon="✈️", layout="wide")

# --- SIDEBAR: Live Simulator ---
st.sidebar.title("🎛️ Command Controls")
st.sidebar.markdown("### 🔮 'What-If' Market Simulator")
sim_fuel = st.sidebar.slider("ATF Fuel Tariff Hike (%)", min_value=0, max_value=30, value=6, step=1)
sim_holiday = st.sidebar.slider("Seasonal Influx Surge (%)", min_value=0, max_value=100, value=25, step=5)

st.sidebar.markdown("---")
selected_airlines = st.sidebar.multiselect("Select Airlines", options=api.airlines, default=api.airlines)

# --- RUN COMPUTATION ---
raw_data = api.get_simulated_data(sim_fuel, sim_holiday)
filtered_raw = raw_data[raw_data['airline'].isin(selected_airlines)]
clean_data = api.clean_fares(filtered_raw)
apix_df = api.calculate_apix(clean_data)

# --- MAIN PAGE UI ---
st.title("✈️ Real-time Airfare Price Index (APIx) - Dashboard")
st.caption("Modular proof-of-concept analytical framework — Built for Team HackHers")
st.write("---")

col_graph, col_explainer = st.columns()

with col_graph:
    st.subheader("📈 Aggregated Index Trajectory")
    st.line_chart(apix_df.set_index('date')[['APIx', 'Weekly_APIx']])

with col_explainer:
    st.subheader("🧠 GraphRAG Explainability")
    test_date = st.selectbox("Select Date to Investigate", apix_df['date'].tolist(), index=21)
    explanation = graph_rag.explain_price_movement(test_date)
    st.info(f"**AI Explanation:** {explanation['explanation']}")
    st.warning(f"**Categories:** {', '.join(explanation['categories'])}")

st.write("---")

col_heat, col_stats = st.columns(2)
with col_heat:
    st.subheader("🌡️ Average Corridor Fares (INR)")
    heat_df = clean_data.groupby(['route', 'lead_time'])['total_fare'].mean().unstack()[['T+1', 'T+7', 'T+15', 'T+30', 'T+45']]
    st.dataframe(heat_df.style.format("₹{:.0f}"))

with col_stats:
    st.subheader("⚙️ System Status")
    st.success(f"✔️ Dynamic Ingestion Layer: Active")
    st.success(f"✔️ Cleaning Logic (IQR): Removed {len(filtered_raw) - len(clean_data)} price outliers")
import streamlit as st
import pandas as pd
import sys
import os

# Dynamic Path Fix: Ensure Python can find parent files
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import apix_prototype as api
from ai_explainability import graph_rag

st.set_page_config(page_title="APIx Command Center", page_icon="✈️", layout="wide")

# --- SIDEBAR: Live Simulator ---
st.sidebar.title("🎛️ Command Controls")
st.sidebar.markdown("### 🔮 'What-If' Market Simulator")
sim_fuel = st.sidebar.slider("ATF Fuel Tariff Hike (%)", min_value=0, max_value=30, value=6, step=1)
sim_holiday = st.sidebar.slider("Seasonal Influx Surge (%)", min_value=0, max_value=100, value=25, step=5)

st.sidebar.markdown("---")
selected_airlines = st.sidebar.multiselect("Select Airlines", options=api.airlines, default=api.airlines)

# --- RUN COMPUTATION ---
raw_data = api.get_simulated_data(sim_fuel, sim_holiday)
filtered_raw = raw_data[raw_data['airline'].isin(selected_airlines)]
clean_data = api.clean_fares(filtered_raw)
apix_df = api.calculate_apix(clean_data)

# --- MAIN PAGE UI ---
st.title("✈️ Real-time Airfare Price Index (APIx) - Dashboard")
st.caption("Modular proof-of-concept analytical framework — Built for Team HackHers")
st.write("---")

col_graph, col_explainer = st.columns()

with col_graph:
    st.subheader("📈 Aggregated Index Trajectory")
    st.line_chart(apix_df.set_index('date')[['APIx', 'Weekly_APIx']])

with col_explainer:
    st.subheader("🧠 GraphRAG Explainability")
    test_date = st.selectbox("Select Date to Investigate", apix_df['date'].tolist(), index=21)
    explanation = graph_rag.explain_price_movement(test_date)
    st.info(f"**AI Explanation:** {explanation['explanation']}")
    st.warning(f"**Categories:** {', '.join(explanation['categories'])}")

st.write("---")

col_heat, col_stats = st.columns(2)
with col_heat:
    st.subheader("🌡️ Average Corridor Fares (INR)")
    heat_df = clean_data.groupby(['route', 'lead_time'])['total_fare'].mean().unstack()[['T+1', 'T+7', 'T+15', 'T+30', 'T+45']]
    st.dataframe(heat_df.style.format("₹{:.0f}"))

with col_stats:
    st.subheader("⚙️ System Status")
    st.success(f"✔️ Dynamic Ingestion Layer: Active")
    st.success(f"✔️ Cleaning Logic (IQR): Removed {len(filtered_raw) - len(clean_data)} price outliers")
