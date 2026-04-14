"""
ML Recommendations Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import fetch_api_json, setup_page_style

setup_page_style()

st.title("🎯 ML Recommendations")
st.markdown("*Personalized scheme recommendations based on risk profile*")

st.subheader("⚙️ Recommendation Options")

col1, col2 = st.columns(2)

with col1:
    risk_profile = st.selectbox("Risk profile", ["low", "moderate", "high"], index=1)

with col2:
    limit = st.slider("Number of recommendations", 3, 20, 5)

if st.button("Get Recommendations", type="primary"):
    data = fetch_api_json(
        "/api/ml/recommendations",
        params={"risk_profile": risk_profile, "limit": limit}
    )

    if data is None:
        st.stop()

    results = pd.DataFrame(data.get("results", []))

    if results.empty:
        st.warning("No recommendations returned.")
        st.stop()

    st.markdown("---")
    st.subheader("✅ Recommended Schemes")

    display = results[[
        "scheme_name",
        "fund_house",
        "utility_score",
        "total_return",
        "volatility",
        "sharpe_ratio",
        "risk_level"
    ]].rename(columns={
        "scheme_name": "Scheme",
        "fund_house": "Fund House",
        "utility_score": "Utility Score",
        "total_return": "Return",
        "volatility": "Volatility",
        "sharpe_ratio": "Sharpe",
        "risk_level": "Risk"
    })

    st.dataframe(display, use_container_width=True, hide_index=True)

    fig = px.bar(
        results,
        x="scheme_name",
        y="utility_score",
        color="risk_level",
        title="Recommendation Utility Scores",
        labels={"scheme_name": "Scheme", "utility_score": "Utility Score"}
    )
    fig.update_xaxes(tickangle=35)
    st.plotly_chart(fig, use_container_width=True)
