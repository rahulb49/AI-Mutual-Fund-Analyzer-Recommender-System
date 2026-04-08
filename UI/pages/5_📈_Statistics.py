"""
Market Statistics & Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    load_featured_data, get_market_stats, get_fund_house_stats,
    format_currency, format_percent, setup_page_style
)

setup_page_style()

st.title("📈 Market Statistics & Analysis")
st.markdown("*Comprehensive market insights and distributions*")

# Load data
@st.cache_resource
def init_data():
    return load_featured_data()

featured_df = init_data()

if featured_df is None:
    st.error("❌ Failed to load data")
    st.stop()

# Get statistics
stats = get_market_stats(featured_df)

# Overall Market Summary
st.subheader("📊 Overall Market Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Schemes", f"{stats['total_schemes']:,}")
col2.metric("Fund Houses", stats['fund_houses'])
col3.metric("Data Points", f"{stats['total_records']:,}")
col4.metric("Active Years", f"{stats['date_range_end'].year - stats['date_range_start'].year + 1}")
col5.metric("Time Span", f"{stats['date_range_start'].date()} to {stats['date_range_end'].date()}")

st.markdown("---")

# NAV Statistics
st.subheader("💰 NAV Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Average NAV", format_currency(stats['avg_nav']))
col2.metric("Median NAV", format_currency(featured_df['net_asset_value'].median()))
col3.metric("Min NAV", format_currency(stats['min_nav']))
col4.metric("Max NAV", format_currency(stats['max_nav']))
col5.metric("Std Dev", format_currency(featured_df['net_asset_value'].std()))

# NAV Distribution Chart
fig = px.histogram(
    featured_df,
    x='net_asset_value',
    nbins=70,
    title="NAV Distribution Across All Schemes",
    labels={'net_asset_value': 'NAV (₹)', 'count': 'Frequency'},
    color_discrete_sequence=['#1f77b4']
)

fig.update_layout(
    xaxis_title="NAV (₹)",
    yaxis_title="Number of Schemes",
    showlegend=False,
    height=400
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Performance Metrics
st.subheader("📈 Performance Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Avg Return", format_percent(stats['avg_return']))
col2.metric("Avg Volatility", format_percent(stats['avg_volatility']))
col3.metric("Avg Sharpe Ratio", f"{stats['avg_sharpe']:.2f}")
col4.metric("Avg Sortino Ratio", f"{featured_df['sortino_ratio_30d'].mean():.2f}")
col5.metric("Avg Max Drawdown", format_percent(featured_df['max_drawdown_1y'].mean()))

st.markdown("---")

# Distribution Analysis
st.subheader("📊 Distribution Analysis")

col1, col2 = st.columns(2)

with col1:
    # Volatility Distribution
    fig = px.histogram(
        featured_df.dropna(subset=['volatility_30d']),
        x='volatility_30d',
        nbins=50,
        title="Volatility Distribution",
        labels={'volatility_30d': 'Volatility %', 'count': 'Number of Schemes'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        xaxis_title="Volatility (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Return Distribution
    fig = px.histogram(
        featured_df.dropna(subset=['cum_return']),
        x='cum_return',
        nbins=50,
        title="Cumulative Return Distribution",
        labels={'cum_return': 'Return %', 'count': 'Number of Schemes'},
        color_discrete_sequence=['#51CF66']
    )
    
    fig.update_layout(
        xaxis_title="Cumulative Return (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Sharpe Ratio Distribution
    fig = px.histogram(
        featured_df.dropna(subset=['sharpe_ratio_30d']),
        x='sharpe_ratio_30d',
        nbins=50,
        title="Sharpe Ratio Distribution",
        labels={'sharpe_ratio_30d': 'Sharpe Ratio', 'count': 'Number of Schemes'},
        color_discrete_sequence=['#FFD93D']
    )
    
    fig.update_layout(
        xaxis_title="Sharpe Ratio",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Daily Return Distribution
    fig = px.histogram(
        featured_df.dropna(subset=['daily_return']),
        x='daily_return',
        nbins=50,
        title="Daily Return Distribution",
        labels={'daily_return': 'Daily Return %', 'count': 'Frequency'},
        color_discrete_sequence=['#6C5CE7']
    )
    
    fig.update_layout(
        xaxis_title="Daily Return (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Percentile Analysis
st.subheader("📊 Percentile Analysis")

percentiles = [10, 25, 50, 75, 90, 95, 99]

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**NAV Percentiles (₹)**")
    
    for p in percentiles:
        value = featured_df['net_asset_value'].quantile(p / 100)
        st.write(f"P{p}: {format_currency(value)}")

with col2:
    st.write("**Volatility Percentiles (%)**")
    
    for p in percentiles:
        value = featured_df['volatility_30d'].quantile(p / 100)
        st.write(f"P{p}: {format_percent(value)}")

with col3:
    st.write("**Return Percentiles (%)**")
    
    for p in percentiles:
        value = featured_df['cum_return'].quantile(p / 100)
        st.write(f"P{p}: {format_percent(value)}")

st.markdown("---")

# Fund House Analysis
st.subheader("🏢 Fund House Analysis")

fund_stats = get_fund_house_stats(featured_df)

col1, col2 = st.columns([2, 1])

with col1:
    # Fund House Chart
    fig = px.bar(
        fund_stats.head(15).reset_index(),
        x='fund_house',
        y='schemes',
        title="Top 15 Fund Houses by Scheme Count",
        labels={'fund_house': 'Fund House', 'schemes': 'Number of Schemes'},
        color='avg_sharpe',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("**Fund House Metrics**")
    st.metric("Total Fund Houses", stats['fund_houses'])
    st.metric("Avg Schemes/FH", f"{stats['total_schemes'] / stats['fund_houses']:.0f}")
    st.metric("Max Schemes", int(fund_stats['schemes'].max()))
    st.metric("Min Schemes", int(fund_stats['schemes'].min()))

st.markdown("---")

# Risk-Return Analysis
st.subheader("⚠️ Risk-Return Profile")

fig = px.scatter(
    featured_df.drop_duplicates('scheme_code', keep='last').dropna(subset=['volatility_30d', 'cum_return']),
    x='volatility_30d',
    y='cum_return',
    size='sharpe_ratio_30d',
    color='sharpe_ratio_30d',
    hover_name='scheme_name',
    hover_data=['fund_house'],
    title="Risk vs Return (Size = Sharpe Ratio)",
    labels={'volatility_30d': 'Volatility (%)', 'cum_return': 'Return (%)'},
    color_continuous_scale='RdYlGn',
    size_max=500
)

fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Time Series Analysis
st.subheader("📉 Market Trends Over Time")

# Aggregate statistics by date
daily_agg = featured_df.groupby('date').agg({
    'net_asset_value': ['mean', 'min', 'max', 'std'],
    'scheme_code': 'count',
    'volatility_30d': 'mean',
    'sharpe_ratio_30d': 'mean'
}).reset_index()

daily_agg.columns = ['date', 'avg_nav', 'min_nav', 'max_nav', 'nav_std', 'active_schemes', 'avg_volatility', 'avg_sharpe']

col1, col2 = st.columns(2)

with col1:
    # NAV Trend
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_agg['date'],
        y=daily_agg['avg_nav'],
        mode='lines',
        name='Average NAV',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_agg['date'],
        y=daily_agg['max_nav'],
        mode='lines',
        name='Max NAV',
        line=dict(color='#51CF66', dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_agg['date'],
        y=daily_agg['min_nav'],
        mode='lines',
        name='Min NAV',
        line=dict(color='#FF6B6B', dash='dash')
    ))
    
    fig.update_layout(
        title="NAV Trends Over Time",
        xaxis_title="Date",
        yaxis_title="NAV (₹)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Volatility Trend
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_agg['date'],
        y=daily_agg['avg_volatility'],
        mode='lines+markers',
        name='Avg Volatility',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=3)
    ))
    
    fig.update_layout(
        title="Average Market Volatility Over Time",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Detailed Statistics Table
st.subheader("📋 Comprehensive Statistics")

summary_stats = {
    'Metric': [
        'Total Schemes',
        'Total Records',
        'Fund Houses',
        'Date Range',
        'Data Span (Years)',
        'Avg NAV',
        'NAV Range',
        'Avg Return',
        'Avg Volatility',
        'Avg Sharpe Ratio',
        'Avg Sortino Ratio',
        'Avg Max Drawdown',
        'Records/Day',
        'Recording Days'
    ],
    'Value': [
        f"{stats['total_schemes']:,}",
        f"{stats['total_records']:,}",
        f"{stats['fund_houses']}",
        f"{stats['date_range_start'].date()} to {stats['date_range_end'].date()}",
        f"{stats['date_range_end'].year - stats['date_range_start'].year + 1}",
        format_currency(stats['avg_nav']),
        f"{format_currency(stats['min_nav'])} - {format_currency(stats['max_nav'])}",
        format_percent(stats['avg_return']),
        format_percent(stats['avg_volatility']),
        f"{stats['avg_sharpe']:.3f}",
        f"{featured_df['sortino_ratio_30d'].mean():.3f}",
        format_percent(featured_df['max_drawdown_1y'].mean()),
        f"{stats['total_records'] / len(daily_agg):.0f}",
        f"{len(daily_agg)}"
    ]
}

st.dataframe(
    pd.DataFrame(summary_stats),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Data Quality
st.subheader("✅ Data Quality")

col1, col2, col3, col4 = st.columns(4)

total_cells = stats['total_records'] * len(featured_df.columns)
null_cells = featured_df.isnull().sum().sum()
completeness = (1 - null_cells / total_cells) * 100

col1.metric("Total Data Points", f"{total_cells:,}")
col2.metric("Missing Values", f"{null_cells:,}")
col3.metric("Data Completeness", f"{completeness:.2f}%")
col4.metric("Data Quality", "✅ Excellent" if completeness > 99 else "⚠️ Good" if completeness > 95 else "❌ Fair")

st.info(
    """
    **Data Notes:**
    - Data sourced from AMFI (Association of Mutual Funds in India)
    - NAV (Net Asset Value) is calculated daily
    - Returns are cumulative from inception
    - Volatility calculated using 30-day rolling window
    - Risk metrics include Sharpe and Sortino ratios
    - All values in Indian Rupees (₹)
    """
)
