import streamlit as st
import pandas as pd
import apix_prototype as api

st.set_page_config(page_title="APIx Dashboard", page_icon="✈️", layout="wide")

st.title("✈️ Real-time Airfare Price Index (APIx)")
st.caption("Simplified proof-of-concept prototype built for Team HackHers")

# Run Pipeline on startup
raw_data = api.get_simulated_data()
clean_data = api.clean_fares(raw_data)
apix_df = api.calculate_apix(clean_data)

# Layout Columns
col_graph, col_explainer = st.columns([2, 1])

with col_graph:
    st.subheader("📈 Daily APIx Trend (Base Period = 100)")
    # Simple line plot of index
    st.line_chart(apix_df.set_index('date')[['APIx', 'Weekly_APIx']])

with col_explainer:
    st.subheader("🧠 GraphRAG Explainability")
    test_date = st.selectbox("Select Date to Investigate", apix_df['date'].tolist(), index=14)
    
    explanation, citations = api.query_explainer(test_date)
    st.info(f"**AI Explanation:** {explanation}")
    if citations:
        st.caption(f"**Sources cited:** {', '.join(citations)}")

st.markdown("---")

# Additional Metrics
col1, col2 = st.columns(2)
with col1:
    st.subheader("🌡️ Average Fares by Route & Window (INR)")
    heat_df = clean_data.groupby(['route', 'lead_time'])['total_fare'].mean().unstack()[['T+1', 'T+7', 'T+15', 'T+30', 'T+45']]
    st.dataframe(heat_df.style.format("₹{:.0f}"))

with col2:
    st.subheader("⚙️ System Operations Status")
    st.success(f"✔️ Active Ingestion: 5 Routes, 5 Airlines, 6 OTAs")
    st.success(f"✔️ Cleaning Logic: Active (Removed {len(raw_data) - len(clean_data)} price outliers)")
