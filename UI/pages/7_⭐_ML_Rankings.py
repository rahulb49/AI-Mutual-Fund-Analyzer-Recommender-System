"""
ML Rankings Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import fetch_api_json, setup_page_style

setup_page_style()

st.title("⭐ ML Rankings")
st.markdown("*Multi-factor ranking using returns, risk, and trend strength*")

st.subheader("⚙️ Ranking Options")

col1, col2 = st.columns(2)

with col1:
    limit = st.slider("Show top", 5, 100, 20)

with col2:
    risk_level = st.selectbox("Risk level filter", ["All", "LOW", "MODERATE", "HIGH"], index=0)

params = {"limit": limit}
if risk_level != "All":
    params["risk_level"] = risk_level

if st.button("Generate Rankings", type="primary"):
    data = fetch_api_json("/api/ml/rankings", params=params)

    if data is None:
        st.stop()

    results = pd.DataFrame(data.get("results", []))

    if results.empty:
        st.warning("No ranking data returned.")
        st.stop()

    st.markdown("---")
    st.subheader("🏆 Top Ranked Schemes")

    display = results[[
        "rank",
        "scheme_name",
        "fund_house",
        "score",
        "total_return",
        "volatility",
        "sharpe_ratio",
        "risk_level"
    ]].rename(columns={
        "rank": "Rank",
        "scheme_name": "Scheme",
        "fund_house": "Fund House",
        "score": "Score",
        "total_return": "Return",
        "volatility": "Volatility",
        "sharpe_ratio": "Sharpe",
        "risk_level": "Risk"
    })

    st.dataframe(display, use_container_width=True, hide_index=True)

    fig = px.bar(
        results.head(20),
        x="rank",
        y="score",
        color="risk_level",
        title="Top 20 Ranking Scores",
        labels={"rank": "Rank", "score": "Score", "risk_level": "Risk"}
    )
    st.plotly_chart(fig, use_container_width=True)
