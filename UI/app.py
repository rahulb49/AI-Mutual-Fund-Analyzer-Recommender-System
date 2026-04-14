"""
NAV Analysis Dashboard - Main Application
Streamlit-based interactive dashboard for analyzing mutual fund data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_featured_data, load_cleaned_data, get_market_stats,
    categorize_risk, categorize_sharpe, format_currency, format_percent,
    setup_page_style, get_fund_house_stats, get_api_status
)

# Page configuration
setup_page_style()

# Sidebar
st.sidebar.title("📊 NAV Analysis Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Dashboard", "🔍 Scheme Analysis", "⚖️ Comparison", "🏆 Rankings", "📈 Statistics"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **About This Dashboard**
    
    Interactive analysis of 14,341 mutual fund schemes across 51 fund houses.
    
    📊 Features:
    - Scheme search & analysis
    - Risk metrics
    - Performance comparison
    - Market statistics
    - Trend analysis
    """
)

# API status badge
api_ok, api_message = get_api_status()
if api_ok:
    st.sidebar.success(f"✅ {api_message}")
else:
    st.sidebar.error(f"❌ {api_message}")

# Load data
@st.cache_resource
def init_data():
    featured = load_featured_data()
    cleaned = load_cleaned_data()
    return featured, cleaned

featured_df, cleaned_df = init_data()

if featured_df is None or cleaned_df is None:
    st.error("❌ Failed to load data. Please ensure data files exist.")
    st.stop()

# ===== Page: Dashboard =====
if page == "🏠 Dashboard":
    st.title("📊 NAV Analysis Dashboard")
    st.markdown("*Real-time analysis of Indian mutual fund schemes*")
    
    # Key Statistics
    st.subheader("📈 Market Overview")
    
    stats = get_market_stats(featured_df)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Schemes", f"{stats['total_schemes']:,}", "Active")
    col2.metric("Fund Houses", stats['fund_houses'], "Distinct")
    col3.metric("Data Points", f"{stats['total_records']:,}", "Records")
    col4.metric("Date Range", f"{stats['date_range_start'].year}-{stats['date_range_end'].year}", "Years")
    
    st.markdown("---")
    
    # NAV Statistics
    st.subheader("💰 NAV Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average NAV", format_currency(stats['avg_nav']))
    col2.metric("Min NAV", format_currency(stats['min_nav']))
    col3.metric("Max NAV", format_currency(stats['max_nav']))
    col4.metric("Median NAV", format_currency(featured_df['net_asset_value'].median()))
    
    st.markdown("---")
    
    # Performance Metrics
    st.subheader("⚠️ Risk & Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Avg Volatility (30d)", f"{stats['avg_volatility']:.2f}%")
        st.caption("Lower is less risky")
    
    with col2:
        st.metric("Avg Sharpe Ratio", f"{stats['avg_sharpe']:.2f}")
        st.caption("Higher is better risk-adjusted return")
    
    st.markdown("---")
    
    # Top Performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⭐ Top 5 by Sharpe Ratio")
        
        top_sharpe = featured_df.dropna(subset=['sharpe_ratio_30d']).drop_duplicates(
            'scheme_code', keep='last'
        ).nlargest(5, 'sharpe_ratio_30d')[['scheme_name', 'sharpe_ratio_30d', 'volatility_30d']]
        
        for idx, (_, row) in enumerate(top_sharpe.iterrows(), 1):
            st.write(
                f"{idx}. **{row['scheme_name'][:40]}**"
                f" | Sharpe: {row['sharpe_ratio_30d']:.2f} | Vol: {row['volatility_30d']:.2f}%"
            )
    
    with col2:
        st.subheader("🚀 Top 5 by Return")
        
        top_return = featured_df.drop_duplicates('scheme_code', keep='last').nlargest(
            5, 'cum_return'
        )[['scheme_name', 'cum_return', 'volatility_30d']]
        
        for idx, (_, row) in enumerate(top_return.iterrows(), 1):
            st.write(
                f"{idx}. **{row['scheme_name'][:40]}**"
                f" | Return: {row['cum_return']:.2f}% | Vol: {row['volatility_30d']:.2f}%"
            )
    
    st.markdown("---")
    
    # Fund House Distribution
    st.subheader("🏢 Fund House Analysis")
    
    fund_stats = get_fund_house_stats(featured_df)
    
    # Chart
    fig = px.bar(
        fund_stats.head(10).reset_index(),
        x='fund_house',
        y='schemes',
        title="Top 10 Fund Houses by Scheme Count",
        labels={'fund_house': 'Fund House', 'schemes': 'Number of Schemes'},
        color='avg_sharpe',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.dataframe(
        fund_stats.head(10).reset_index().rename(columns={
            'fund_house': 'Fund House',
            'schemes': 'Schemes',
            'avg_nav': 'Avg NAV',
            'avg_volatility': 'Avg Vol %',
            'avg_sharpe': 'Avg Sharpe'
        }),
        use_container_width=True,
        hide_index=True
    )

# ===== Page: Scheme Analysis =====
elif page == "🔍 Scheme Analysis":
    st.title("🔍 Scheme Analysis")
    
    # Search
    search_query = st.text_input(
        "Search for a scheme",
        placeholder="Enter scheme name or fund house..."
    )
    
    schemes = (featured_df.drop_duplicates('scheme_code', keep='last')
               .sort_values('scheme_name'))
    
    if search_query:
        schemes = schemes[
            schemes['scheme_name'].str.contains(search_query, case=False, na=False) |
            schemes['fund_house'].str.contains(search_query, case=False, na=False)
        ]
    
    if len(schemes) == 0:
        st.warning("No schemes found matching your search.")
    else:
        # Select scheme
        selected_scheme = st.selectbox(
            "Select a scheme:",
            schemes['scheme_name'].values,
            key="scheme_select"
        )
        
        if selected_scheme:
            scheme_code = schemes[schemes['scheme_name'] == selected_scheme]['scheme_code'].iloc[0]
            scheme_data = featured_df[featured_df['scheme_code'] == scheme_code]
            
            if len(scheme_data) > 0:
                latest = scheme_data.iloc[-1]
                
                # Header
                col1, col2 = st.columns([3, 1])
                col1.title(selected_scheme)
                col2.metric("Fund House", latest['fund_house'])
                
                st.markdown("---")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Current NAV", format_currency(latest['net_asset_value']))
                col2.metric("Cumulative Return", format_percent(latest.get('cum_return', 0)))
                col3.metric("Volatility (30d)", format_percent(latest.get('volatility_30d', 0)))
                col4.metric("Sharpe Ratio", f"{latest.get('sharpe_ratio_30d', 0):.2f}")
                
                st.markdown("---")
                
                # Risk Profile
                st.subheader("⚠️ Risk Profile")
                
                col1, col2, col3 = st.columns(3)
                
                volatility = latest.get('volatility_30d', 0)
                sharpe = latest.get('sharpe_ratio_30d', 0)
                drawdown = latest.get('max_drawdown_1y', 0)
                
                col1.write(f"**Risk Level**: {categorize_risk(volatility)}")
                col2.write(f"**Risk-Adjusted Return**: {categorize_sharpe(sharpe)}")
                col3.write(f"**Max Drawdown**: {format_percent(drawdown)}")
                
                st.markdown("---")
                
                # Trend Analysis
                st.subheader("📊 Trend Analysis")
                
                col1, col2, col3, col4 = st.columns(4)
                
                trend_dir = "Uptrend ⬆️" if latest.get('trend_slope', 0) > 0 else "Downtrend ⬇️"
                col1.metric("Trend Direction", trend_dir)
                col2.metric("Trend Strength (R²)", f"{latest.get('trend_strength', 0):.4f}")
                col3.metric("RSI (14)", f"{latest.get('rsi_14', 50):.0f}")
                col4.metric("Golden Cross", "✓ Yes" if latest.get('golden_cross', 0) else "✗ No")
                
                st.markdown("---")
                
                # NAV Chart
                st.subheader("📈 NAV History")
                
                scheme_sorted = scheme_data.sort_values('date')
                
                fig = px.line(
                    scheme_sorted.tail(100),
                    x='date',
                    y='net_asset_value',
                    title="NAV Over Time (Last 100 records)",
                    labels={'date': 'Date', 'net_asset_value': 'NAV (₹)'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary Stats
                st.subheader("📋 Summary Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Min NAV", format_currency(scheme_data['net_asset_value'].min()))
                col2.metric("Max NAV", format_currency(scheme_data['net_asset_value'].max()))
                col3.metric("Avg NAV", format_currency(scheme_data['net_asset_value'].mean()))
                col4.metric("Data Points", len(scheme_data))

# ===== Page: Comparison =====
elif page == "⚖️ Comparison":
    st.title("⚖️ Scheme Comparison")
    
    # Multi-select schemes
    schemes_list = featured_df.drop_duplicates(
        'scheme_code', keep='last'
    ).sort_values('scheme_name')['scheme_name'].values
    
    selected_schemes = st.multiselect(
        "Select schemes to compare (2-5):",
        schemes_list,
        max_selections=5,
        key="compare_select"
    )
    
    if len(selected_schemes) < 2:
        st.warning("Please select at least 2 schemes to compare.")
    else:
        # Get data for selected schemes
        comparison_data = []
        
        for scheme in selected_schemes:
            scheme_code = featured_df[featured_df['scheme_name'] == scheme][
                'scheme_code'
            ].iloc[0]
            scheme_latest = featured_df[featured_df['scheme_code'] == scheme_code].iloc[-1]
            
            comparison_data.append({
                'Scheme': scheme[:30],
                'Fund House': scheme_latest['fund_house'],
                'Current NAV': scheme_latest['net_asset_value'],
                'Return %': scheme_latest.get('cum_return', 0),
                'Volatility %': scheme_latest.get('volatility_30d', 0),
                'Sharpe Ratio': scheme_latest.get('sharpe_ratio_30d', 0),
                'Sortino Ratio': scheme_latest.get('sortino_ratio_30d', 0),
                'Max Drawdown %': scheme_latest.get('max_drawdown_1y', 0),
            })
        
        comp_df = pd.DataFrame(comparison_data)
        
        # Display table
        st.subheader("Comparison Table")
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Return vs Volatility
            fig = px.scatter(
                comp_df,
                x='Volatility %',
                y='Return %',
                size='Sharpe Ratio',
                hover_name='Scheme',
                title="Return vs Risk (Volatility)",
                color='Sharpe Ratio',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sharpe Ratio Comparison
            fig = px.bar(
                comp_df,
                x='Scheme',
                y='Sharpe Ratio',
                title="Sharpe Ratio Comparison",
                color='Sharpe Ratio',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== Page: Rankings =====
elif page == "🏆 Rankings":
    st.title("🏆 Scheme Rankings")
    
    ranking_metric = st.selectbox(
        "Rank by:",
        ["Sharpe Ratio", "Return", "Volatility (Low to High)", "NAV"],
        key="ranking_select"
    )
    
    ranking_limit = st.slider("Number of schemes to show:", 5, 50, 10)
    
    st.markdown("---")
    
    if ranking_metric == "Sharpe Ratio":
        top_schemes = featured_df.dropna(subset=['sharpe_ratio_30d']).drop_duplicates(
            'scheme_code', keep='last'
        ).nlargest(ranking_limit, 'sharpe_ratio_30d')
        
        st.subheader(f"Top {ranking_limit} Schemes by Sharpe Ratio")
        
        ranking_df = top_schemes[[
            'scheme_name', 'fund_house', 'sharpe_ratio_30d', 'volatility_30d', 'cum_return'
        ]].reset_index(drop=True)
        ranking_df.index = ranking_df.index + 1
        
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='sharpe_ratio_30d',
            title="Sharpe Ratio Rankings",
            labels={'index': 'Rank', 'sharpe_ratio_30d': 'Sharpe Ratio'},
            color='sharpe_ratio_30d',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(ranking_df, use_container_width=True)
    
    elif ranking_metric == "Return":
        top_schemes = featured_df.drop_duplicates('scheme_code', keep='last').nlargest(
            ranking_limit, 'cum_return'
        )
        
        st.subheader(f"Top {ranking_limit} Schemes by Return")
        
        ranking_df = top_schemes[[
            'scheme_name', 'fund_house', 'cum_return', 'volatility_30d', 'sharpe_ratio_30d'
        ]].reset_index(drop=True)
        ranking_df.index = ranking_df.index + 1
        
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='cum_return',
            title="Return Rankings",
            labels={'index': 'Rank', 'cum_return': 'Cumulative Return %'},
            color='cum_return',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(ranking_df, use_container_width=True)
    
    elif ranking_metric == "Volatility (Low to High)":
        top_schemes = featured_df.dropna(subset=['volatility_30d']).drop_duplicates(
            'scheme_code', keep='last'
        ).nsmallest(ranking_limit, 'volatility_30d')
        
        st.subheader(f"Lowest {ranking_limit} Volatility Schemes")
        
        ranking_df = top_schemes[[
            'scheme_name', 'fund_house', 'volatility_30d', 'sharpe_ratio_30d', 'cum_return'
        ]].reset_index(drop=True)
        ranking_df.index = ranking_df.index + 1
        
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='volatility_30d',
            title="Lowest Volatility (Least Risk)",
            labels={'index': 'Rank', 'volatility_30d': 'Volatility %'},
            color='volatility_30d',
            color_continuous_scale='Viridis_r'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(ranking_df, use_container_width=True)
    
    elif ranking_metric == "NAV":
        top_schemes = featured_df.drop_duplicates('scheme_code', keep='last').nlargest(
            ranking_limit, 'net_asset_value'
        )
        
        st.subheader(f"Highest {ranking_limit} NAV Schemes")
        
        ranking_df = top_schemes[[
            'scheme_name', 'fund_house', 'net_asset_value', 'cum_return', 'volatility_30d'
        ]].reset_index(drop=True)
        ranking_df.index = ranking_df.index + 1
        
        fig = px.bar(
            ranking_df.reset_index(),
            x='index',
            y='net_asset_value',
            title="Highest NAV",
            labels={'index': 'Rank', 'net_asset_value': 'NAV (₹)'},
            color='net_asset_value',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(ranking_df, use_container_width=True)

# ===== Page: Statistics =====
elif page == "📈 Statistics":
    st.title("📈 Market Statistics & Analysis")
    
    st.subheader("📊 Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # NAV Distribution
        fig = px.histogram(
            featured_df,
            x='net_asset_value',
            nbins=50,
            title="NAV Distribution",
            labels={'net_asset_value': 'NAV (₹)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Volatility Distribution
        fig = px.histogram(
            featured_df.dropna(subset=['volatility_30d']),
            x='volatility_30d',
            nbins=50,
            title="Volatility Distribution",
            labels={'volatility_30d': 'Volatility %'},
            color_discrete_sequence=['#FF6B6B']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Return Distribution
        fig = px.histogram(
            featured_df.dropna(subset=['cum_return']),
            x='cum_return',
            nbins=50,
            title="Cumulative Return Distribution",
            labels={'cum_return': 'Return %'},
            color_discrete_sequence=['#51CF66']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sharpe Ratio Distribution
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
    
    st.subheader("📋 Detailed Statistics")
    
    stats_dict = {
        'Metric': [
            'Total Schemes',
            'Total Records',
            'Fund Houses',
            'Date Range',
            'Avg NAV',
            'Min NAV',
            'Max NAV',
            'Avg Return',
            'Avg Volatility',
            'Avg Sharpe Ratio'
        ],
        'Value': [
            f"{featured_df['scheme_code'].nunique():,}",
            f"{len(featured_df):,}",
            f"{featured_df['fund_house'].nunique()}",
            f"{featured_df['date'].min().date()} to {featured_df['date'].max().date()}",
            format_currency(featured_df['net_asset_value'].mean()),
            format_currency(featured_df['net_asset_value'].min()),
            format_currency(featured_df['net_asset_value'].max()),
            format_percent(featured_df['cum_return'].mean()) if 'cum_return' in featured_df.columns else 'N/A',
            format_percent(featured_df['volatility_30d'].mean()) if 'volatility_30d' in featured_df.columns else 'N/A',
            f"{featured_df['sharpe_ratio_30d'].mean():.2f}" if 'sharpe_ratio_30d' in featured_df.columns else 'N/A'
        ]
    }
    
    st.dataframe(
        pd.DataFrame(stats_dict),
        use_container_width=True,
        hide_index=True
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Dashboard Version**: 1.0.0\n\n"
    "**Last Updated**: April 9, 2026\n\n"
    "[📖 Documentation]() | [🔗 API](http://localhost:8000/docs)"
)
