"""
ML Clustering Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import fetch_api_json, setup_page_style

setup_page_style()

st.title("🤖 ML Clustering")
st.markdown("*Cluster funds based on risk-return features for discovery*")

st.subheader("⚙️ Clustering Options")

col1, col2 = st.columns(2)

with col1:
    n_clusters = st.slider("Number of clusters", 2, 10, 4)

with col2:
    random_state = st.number_input("Random seed", min_value=0, max_value=9999, value=42)

if st.button("Run Clustering", type="primary"):
    data = fetch_api_json(
        "/api/ml/clusters",
        params={"n_clusters": n_clusters, "random_state": random_state}
    )

    if data is None:
        st.stop()

    clusters = pd.DataFrame(data.get("clusters", []))
    sample = pd.DataFrame(data.get("sample", []))

    if clusters.empty:
        st.warning("No cluster data returned.")
        st.stop()

    st.markdown("---")
    st.subheader("📊 Cluster Summary")

    clusters_display = clusters.rename(columns={
        "cluster_id": "Cluster",
        "count": "Schemes",
        "avg_return": "Avg Return",
        "avg_volatility": "Avg Volatility",
        "avg_sharpe": "Avg Sharpe",
        "avg_drawdown": "Avg Drawdown"
    })

    st.dataframe(clusters_display, use_container_width=True, hide_index=True)

    fig = px.scatter(
        clusters,
        x="avg_volatility",
        y="avg_return",
        size="count",
        color="cluster_id",
        title="Cluster Risk vs Return",
        labels={
            "avg_volatility": "Avg Volatility",
            "avg_return": "Avg Return",
            "cluster_id": "Cluster"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🔎 Sample Schemes")

    if not sample.empty:
        sample_display = sample[[
            "scheme_name",
            "fund_house",
            "total_return",
            "volatility",
            "sharpe_ratio",
            "risk_level",
            "cluster_id"
        ]].rename(columns={
            "scheme_name": "Scheme",
            "fund_house": "Fund House",
            "total_return": "Return",
            "volatility": "Volatility",
            "sharpe_ratio": "Sharpe",
            "risk_level": "Risk",
            "cluster_id": "Cluster"
        })

        st.dataframe(sample_display.head(50), use_container_width=True, hide_index=True)
    else:
        st.info("No sample data available.")
