"""
Dashboard - Market Overview Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    load_featured_data, get_market_stats, categorize_risk,
    format_currency, setup_page_style, get_fund_house_stats
)

setup_page_style()

st.title("📊 Dashboard")
st.markdown("*Real-time analysis of the mutual fund market*")

# Load data
@st.cache_resource
def init_data():
    return load_featured_data()

featured_df = init_data()

if featured_df is None:
    st.error("❌ Failed to load data")
    st.stop()

# Key Statistics
st.subheader("📈 Market Overview")

stats = get_market_stats(featured_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Schemes", f"{stats['total_schemes']:,}")
col2.metric("Fund Houses", stats['fund_houses'])
col3.metric("Data Points", f"{stats['total_records']:,}")
col4.metric("Active Years", f"{stats['date_range_end'].year - stats['date_range_start'].year + 1}")

st.markdown("---")

# NAV Overview
st.subheader("💰 NAV Market Analysis")

col1, col2, col3 = st.columns(3)
col1.metric("Average NAV", format_currency(stats['avg_nav']))
col2.metric("Min - Max NAV", f"{format_currency(stats['min_nav'])} - {format_currency(stats['max_nav'])}")
col3.metric("Median NAV", format_currency(featured_df['net_asset_value'].median()))

# NAV Distribution
fig = px.histogram(
    featured_df,
    x='net_asset_value',
    nbins=60,
    title="NAV Distribution Across All Schemes",
    labels={'net_asset_value': 'NAV (₹)', 'count': 'Frequency'}
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Risk & Performance
st.subheader("⚠️ Risk & Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Volatility", f"{stats['avg_volatility']:.2f}%")
col2.metric("Avg Sharpe Ratio", f"{stats['avg_sharpe']:.2f}")
col3.metric("Total Schemes", f"{stats['total_schemes']:,}")
col4.metric("Risk Profile", "🟠 Moderate")

# Performance Distribution
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        featured_df.dropna(subset=['volatility_30d']),
        x='volatility_30d',
        nbins=50,
        title="Volatility Distribution",
        labels={'volatility_30d': 'Volatility %'},
        color_discrete_sequence=['#FF6B6B']
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        featured_df.dropna(subset=['sharpe_ratio_30d']),
        x='sharpe_ratio_30d',
        nbins=50,
        title="Sharpe Ratio Distribution",
        labels={'sharpe_ratio_30d': 'Sharpe Ratio'},
        color_discrete_sequence=['#FFD93D']
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Top Fund Houses
st.subheader("🏢 Fund House Leaders")

fund_stats = get_fund_house_stats(featured_df)
top_funds = fund_stats.head(10).reset_index()

col1, col2 = st.columns([1.5, 1])

with col1:
    fig = px.bar(
        top_funds,
        x='fund_house',
        y='schemes',
        title="Top 10 Fund Houses by Scheme Count",
        labels={'fund_house': 'Fund House', 'schemes': 'Number of Schemes'},
        color='avg_sharpe',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.metric("Leader by Schemes", top_funds.iloc[0]['fund_house'])
    st.metric("Schemes", int(top_funds.iloc[0]['schemes']))
    st.metric("Avg Sharpe", f"{top_funds.iloc[0]['avg_sharpe']:.2f}")

# Detailed Fund House Table
st.subheader("Fund House Statistics")

display_df = fund_stats.head(15).reset_index().rename(columns={
    'fund_house': 'Fund House',
    'schemes': 'Schemes',
    'avg_nav': 'Avg NAV',
    'avg_volatility': 'Volatility %',
    'avg_sharpe': 'Sharpe Ratio'
})

st.dataframe(
    display_df[[col for col in display_df.columns if col != 'index']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Market Timeline
st.subheader("📅 Market Timeline")

daily_stats = featured_df.groupby('date').agg({
    'net_asset_value': 'mean',
    'volatility_30d': 'mean',
    'scheme_code': 'count'
}).reset_index()
daily_stats.columns = ['date', 'avg_nav', 'avg_volatility', 'active_schemes']

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily_stats['date'],
    y=daily_stats['avg_nav'],
    mode='lines',
    name='Avg NAV',
    yaxis='y1'
))

fig.update_layout(
    title="Average NAV Trend Over Time",
    xaxis_title="Date",
    yaxis_title="Average NAV (₹)",
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig, use_container_width=True)
