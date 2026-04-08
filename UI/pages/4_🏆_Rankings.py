"""
Scheme Rankings Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    load_featured_data, format_currency, format_percent, setup_page_style
)

setup_page_style()

st.title("🏆 Scheme Rankings")
st.markdown("*Top performing schemes across different metrics*")

# Load data
@st.cache_resource
def init_data():
    return load_featured_data()

featured_df = init_data()

if featured_df is None:
    st.error("❌ Failed to load data")
    st.stop()

# Ranking selection
st.subheader("🎯 Ranking Options")

col1, col2 = st.columns([2, 1])

with col1:
    ranking_metric = st.radio(
        "Select ranking metric:",
        [
            "Sharpe Ratio (Risk-Adjusted Return)",
            "Cumulative Return",
            "Volatility (Low to High)",
            "Sortino Ratio",
            "NAV",
            "Fund House Size"
        ],
        index=0,
        horizontal=False,
        key="ranking_metric"
    )

with col2:
    ranking_limit = st.slider("Show top:", 5, 50, 10, key="ranking_limit")

st.markdown("---")

# ===== Sharpe Ratio Rankings =====
if ranking_metric == "Sharpe Ratio (Risk-Adjusted Return)":
    st.subheader(f"🏆 Top {ranking_limit} Schemes by Sharpe Ratio")
    st.markdown("*Higher Sharpe Ratio = Better risk-adjusted return*")
    
    top_schemes = featured_df.dropna(subset=['sharpe_ratio_30d']).drop_duplicates(
        'scheme_code', keep='last'
    ).nlargest(ranking_limit, 'sharpe_ratio_30d')
    
    ranking_df = top_schemes[[
        'scheme_name', 'fund_house', 'sharpe_ratio_30d', 'volatility_30d',
        'cum_return', 'net_asset_value'
    ]].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='sharpe_ratio_30d',
            title=f"Top {ranking_limit} Schemes by Sharpe Ratio",
            labels={'index': 'Rank', 'sharpe_ratio_30d': 'Sharpe Ratio'},
            color='sharpe_ratio_30d',
            color_continuous_scale='Viridis'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Top Scheme Sharpe", f"{ranking_df.iloc[0]['sharpe_ratio_30d']:.3f}")
        st.metric("Avg Sharpe (Top 10)", f"{ranking_df.iloc[:10]['sharpe_ratio_30d'].mean():.3f}")
        st.metric("Market Avg Sharpe",
                  f"{featured_df['sharpe_ratio_30d'].mean():.3f}")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = ranking_df.rename(columns={
        'scheme_name': 'Scheme',
        'fund_house': 'Fund House',
        'sharpe_ratio_30d': 'Sharpe Ratio',
        'volatility_30d': 'Volatility %',
        'cum_return': 'Return %',
        'net_asset_value': 'NAV'
    }).copy()
    
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:.3f}")
    display_df['Volatility %'] = display_df['Volatility %'].apply(lambda x: f"{x:.2f}%")
    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:.2f}%")
    display_df['NAV'] = display_df['NAV'].apply(lambda x: f"₹{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)

# ===== Return Rankings =====
elif ranking_metric == "Cumulative Return":
    st.subheader(f"🚀 Top {ranking_limit} Schemes by Return")
    st.markdown("*Highest cumulative returns*")
    
    top_schemes = featured_df.drop_duplicates('scheme_code', keep='last').nlargest(
        ranking_limit, 'cum_return'
    )
    
    ranking_df = top_schemes[[
        'scheme_name', 'fund_house', 'cum_return', 'volatility_30d',
        'sharpe_ratio_30d', 'net_asset_value'
    ]].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='cum_return',
            title=f"Top {ranking_limit} Schemes by Return",
            labels={'index': 'Rank', 'cum_return': 'Return %'},
            color='cum_return',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Top Return", f"{ranking_df.iloc[0]['cum_return']:.2f}%")
        st.metric("Avg Return (Top 10)", f"{ranking_df.iloc[:10]['cum_return'].mean():.2f}%")
        st.metric("Market Avg Return", f"{featured_df['cum_return'].mean():.2f}%")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = ranking_df.rename(columns={
        'scheme_name': 'Scheme',
        'fund_house': 'Fund House',
        'cum_return': 'Return %',
        'volatility_30d': 'Volatility %',
        'sharpe_ratio_30d': 'Sharpe Ratio',
        'net_asset_value': 'NAV'
    }).copy()
    
    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:.2f}%")
    display_df['Volatility %'] = display_df['Volatility %'].apply(lambda x: f"{x:.2f}%")
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:.3f}")
    display_df['NAV'] = display_df['NAV'].apply(lambda x: f"₹{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)

# ===== Volatility Rankings =====
elif ranking_metric == "Volatility (Low to High)":
    st.subheader(f"🛡️ {ranking_limit} Lowest Volatility Schemes")
    st.markdown("*Lowest risk schemes*")
    
    top_schemes = featured_df.dropna(subset=['volatility_30d']).drop_duplicates(
        'scheme_code', keep='last'
    ).nsmallest(ranking_limit, 'volatility_30d')
    
    ranking_df = top_schemes[[
        'scheme_name', 'fund_house', 'volatility_30d', 'sharpe_ratio_30d',
        'cum_return', 'net_asset_value'
    ]].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='volatility_30d',
            title=f"Top {ranking_limit} Lowest Volatility Schemes",
            labels={'index': 'Rank', 'volatility_30d': 'Volatility %'},
            color='volatility_30d',
            color_continuous_scale='Viridis_r'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Lowest Volatility", f"{ranking_df.iloc[0]['volatility_30d']:.2f}%")
        st.metric("Avg Volatility (Top 10)", f"{ranking_df.iloc[:10]['volatility_30d'].mean():.2f}%")
        st.metric("Market Avg Vol", f"{featured_df['volatility_30d'].mean():.2f}%")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = ranking_df.rename(columns={
        'scheme_name': 'Scheme',
        'fund_house': 'Fund House',
        'volatility_30d': 'Volatility %',
        'sharpe_ratio_30d': 'Sharpe Ratio',
        'cum_return': 'Return %',
        'net_asset_value': 'NAV'
    }).copy()
    
    display_df['Volatility %'] = display_df['Volatility %'].apply(lambda x: f"{x:.2f}%")
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:.3f}")
    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:.2f}%")
    display_df['NAV'] = display_df['NAV'].apply(lambda x: f"₹{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)

# ===== Sortino Ratio Rankings =====
elif ranking_metric == "Sortino Ratio":
    st.subheader(f"⭐ Top {ranking_limit} Schemes by Sortino Ratio")
    st.markdown("*Better downside risk-adjusted return*")
    
    top_schemes = featured_df.dropna(subset=['sortino_ratio_30d']).drop_duplicates(
        'scheme_code', keep='last'
    ).nlargest(ranking_limit, 'sortino_ratio_30d')
    
    ranking_df = top_schemes[[
        'scheme_name', 'fund_house', 'sortino_ratio_30d', 'sharpe_ratio_30d',
        'volatility_30d', 'net_asset_value'
    ]].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='sortino_ratio_30d',
            title=f"Top {ranking_limit} Schemes by Sortino Ratio",
            labels={'index': 'Rank', 'sortino_ratio_30d': 'Sortino Ratio'},
            color='sortino_ratio_30d',
            color_continuous_scale='Viridis'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Top Sortino", f"{ranking_df.iloc[0]['sortino_ratio_30d']:.3f}")
        st.metric("Avg Sortino (Top 10)", f"{ranking_df.iloc[:10]['sortino_ratio_30d'].mean():.3f}")
        st.metric("Market Avg Sortino",
                  f"{featured_df['sortino_ratio_30d'].mean():.3f}")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = ranking_df.rename(columns={
        'scheme_name': 'Scheme',
        'fund_house': 'Fund House',
        'sortino_ratio_30d': 'Sortino Ratio',
        'sharpe_ratio_30d': 'Sharpe Ratio',
        'volatility_30d': 'Volatility %',
        'net_asset_value': 'NAV'
    }).copy()
    
    display_df['Sortino Ratio'] = display_df['Sortino Ratio'].apply(lambda x: f"{x:.3f}")
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:.3f}")
    display_df['Volatility %'] = display_df['Volatility %'].apply(lambda x: f"{x:.2f}%")
    display_df['NAV'] = display_df['NAV'].apply(lambda x: f"₹{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)

# ===== NAV Rankings =====
elif ranking_metric == "NAV":
    st.subheader(f"💰 Top {ranking_limit} Schemes by NAV")
    st.markdown("*Highest Net Asset Value*")
    
    top_schemes = featured_df.drop_duplicates('scheme_code', keep='last').nlargest(
        ranking_limit, 'net_asset_value'
    )
    
    ranking_df = top_schemes[[
        'scheme_name', 'fund_house', 'net_asset_value', 'cum_return',
        'volatility_30d', 'sharpe_ratio_30d'
    ]].reset_index(drop=True)
    ranking_df.index = ranking_df.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='net_asset_value',
            title=f"Top {ranking_limit} Schemes by NAV",
            labels={'index': 'Rank', 'net_asset_value': 'NAV (₹)'},
            color='net_asset_value',
            color_continuous_scale='Blues'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Highest NAV", f"₹{ranking_df.iloc[0]['net_asset_value']:.2f}")
        st.metric("Avg NAV (Top 10)", f"₹{ranking_df.iloc[:10]['net_asset_value'].mean():.2f}")
        st.metric("Market Avg NAV", f"₹{featured_df['net_asset_value'].mean():.2f}")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = ranking_df.rename(columns={
        'scheme_name': 'Scheme',
        'fund_house': 'Fund House',
        'net_asset_value': 'NAV',
        'cum_return': 'Return %',
        'volatility_30d': 'Volatility %',
        'sharpe_ratio_30d': 'Sharpe Ratio'
    }).copy()
    
    display_df['NAV'] = display_df['NAV'].apply(lambda x: f"₹{x:.2f}")
    display_df['Return %'] = display_df['Return %'].apply(lambda x: f"{x:.2f}%")
    display_df['Volatility %'] = display_df['Volatility %'].apply(lambda x: f"{x:.2f}%")
    display_df['Sharpe Ratio'] = display_df['Sharpe Ratio'].apply(lambda x: f"{x:.3f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)

# ===== Fund House Rankings =====
else:  # Fund House Size
    st.subheader(f"🏢 Top {ranking_limit} Fund Houses by Scheme Count")
    st.markdown("*Largest fund houses with most schemes*")
    
    fund_stats = featured_df.drop_duplicates('scheme_code', keep='last').groupby('fund_house').agg({
        'scheme_code': 'count',
        'net_asset_value': 'mean',
        'sharpe_ratio_30d': 'mean',
        'volatility_30d': 'mean',
        'cum_return': 'mean'
    }).reset_index()
    
    fund_stats.columns = ['fund_house', 'schemes', 'avg_nav', 'avg_sharpe', 'avg_volatility', 'avg_return']
    fund_stats = fund_stats.nlargest(ranking_limit, 'schemes')
    fund_stats.index = fund_stats.index + 1
    
    # Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = px.bar(
            fund_stats.reset_index(),
            x='index',
            y='schemes',
            title=f"Top {ranking_limit} Fund Houses by Scheme Count",
            labels={'index': 'Rank', 'schemes': 'Number of Schemes'},
            color='avg_sharpe',
            color_continuous_scale='Viridis'
        )
        
        fig.update_xaxes(title_text="Rank")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("Top Fund House", fund_stats.iloc[0]['fund_house'])
        st.metric("Schemes", int(fund_stats.iloc[0]['schemes']))
        st.metric("Avg Sharpe", f"{fund_stats.iloc[0]['avg_sharpe']:.3f}")
    
    # Table
    st.subheader("📋 Detailed Rankings")
    
    display_df = fund_stats.rename(columns={
        'fund_house': 'Fund House',
        'schemes': 'Schemes',
        'avg_nav': 'Avg NAV',
        'avg_sharpe': 'Avg Sharpe',
        'avg_volatility': 'Avg Vol %',
        'avg_return': 'Avg Return %'
    }).copy()
    
    display_df['Avg NAV'] = display_df['Avg NAV'].apply(lambda x: f"₹{x:.2f}")
    display_df['Avg Sharpe'] = display_df['Avg Sharpe'].apply(lambda x: f"{x:.3f}")
    display_df['Avg Vol %'] = display_df['Avg Vol %'].apply(lambda x: f"{x:.2f}%")
    display_df['Avg Return %'] = display_df['Avg Return %'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=False)
