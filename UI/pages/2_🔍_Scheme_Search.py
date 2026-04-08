"""
Scheme Search & Analysis Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    load_featured_data, categorize_risk, categorize_sharpe,
    format_currency, format_percent, setup_page_style
)

setup_page_style()

st.title("🔍 Scheme Search & Analysis")
st.markdown("*Find and analyze individual mutual fund schemes*")

# Load data
@st.cache_resource
def init_data():
    return load_featured_data()

featured_df = init_data()

if featured_df is None:
    st.error("❌ Failed to load data")
    st.stop()

# Filters
st.subheader("🔎 Search Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input(
        "Search by scheme name or fund house",
        placeholder="Type to search...",
        key="search_input"
    )

with col2:
    fund_houses = sorted(featured_df['fund_house'].unique())
    selected_fund_house = st.selectbox(
        "Filter by Fund House",
        ["All"] + fund_houses,
        key="fund_house_filter"
    )

with col3:
    min_nav, max_nav = st.slider(
        "NAV Range (₹)",
        float(featured_df['net_asset_value'].min()),
        float(featured_df['net_asset_value'].max()),
        (float(featured_df['net_asset_value'].quantile(0.25)),
         float(featured_df['net_asset_value'].quantile(0.75))),
        key="nav_range"
    )

# Apply filters
schemes = featured_df.drop_duplicates('scheme_code', keep='last').copy()

if search_query:
    schemes = schemes[
        schemes['scheme_name'].str.contains(search_query, case=False, na=False) |
        schemes['fund_house'].str.contains(search_query, case=False, na=False)
    ]

if selected_fund_house != "All":
    schemes = schemes[schemes['fund_house'] == selected_fund_house]

schemes = schemes[
    (schemes['net_asset_value'] >= min_nav) &
    (schemes['net_asset_value'] <= max_nav)
]

schemes = schemes.sort_values('scheme_name')

st.markdown(f"**Found {len(schemes)} schemes**")
st.markdown("---")

if len(schemes) == 0:
    st.warning("No schemes match your filters. Try adjusting the search criteria.")
else:
    # Scheme selection
    selected_scheme_name = st.selectbox(
        "Select a scheme to analyze:",
        schemes['scheme_name'].values,
        key="scheme_analysis_select"
    )
    
    if selected_scheme_name:
        scheme_code = schemes[schemes['scheme_name'] == selected_scheme_name]['scheme_code'].iloc[0]
        scheme_full_data = featured_df[featured_df['scheme_code'] == scheme_code].sort_values('date')
        latest = scheme_full_data.iloc[-1]
        
        # Header with scheme name and fund house
        col1, col2, col3 = st.columns([2, 1, 1])
        
        col1.markdown(f"## {selected_scheme_name}")
        col2.metric("Fund House", latest['fund_house'])
        col3.metric("Data Points", len(scheme_full_data))
        
        st.markdown("---")
        
        # Key Metrics
        st.subheader("📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Current NAV", format_currency(latest['net_asset_value']))
        col2.metric("NAV 30d Avg", format_currency(
            scheme_full_data['net_asset_value'].tail(30).mean()
        ))
        col3.metric("Min NAV", format_currency(scheme_full_data['net_asset_value'].min()))
        col4.metric("Max NAV", format_currency(scheme_full_data['net_asset_value'].max()))
        
        st.markdown("---")
        
        # Performance Metrics
        st.subheader("📈 Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        cum_return = latest.get('cum_return', 0)
        daily_return = latest.get('daily_return', 0)
        volatility = latest.get('volatility_30d', 0)
        sharpe = latest.get('sharpe_ratio_30d', 0)
        
        col1.metric("Cumulative Return", format_percent(cum_return))
        col2.metric("Daily Return", format_percent(daily_return))
        col3.metric("Volatility (30d)", format_percent(volatility))
        col4.metric("Sharpe Ratio", f"{sharpe:.3f}")
        
        st.markdown("---")
        
        # Risk Assessment
        st.subheader("⚠️ Risk Assessment")
        
        col1, col2, col3 = st.columns(3)
        
        col1.write(f"""
        **Risk Level**: {categorize_risk(volatility)}
        
        **Volatility**: {format_percent(volatility)}
        """)
        
        col2.write(f"""
        **Risk-Adjusted Return**: {categorize_sharpe(sharpe)}
        
        **Sharpe Ratio**: {sharpe:.3f}
        """)
        
        col3.write(f"""
        **Max Drawdown**: {format_percent(latest.get('max_drawdown_1y', 0))}
        
        **Sortino Ratio**: {latest.get('sortino_ratio_30d', 0):.3f}
        """)
        
        st.markdown("---")
        
        # Trend Analysis
        st.subheader("📉 Trend Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        trend_slope = latest.get('trend_slope', 0)
        trend_dir = "Uptrend ⬆️" if trend_slope > 0 else "Downtrend ⬇️"
        
        col1.metric("Trend Direction", trend_dir)
        col2.metric("Trend Strength (R²)", f"{latest.get('trend_strength', 0):.4f}")
        col3.metric("RSI (14)", f"{latest.get('rsi_14', 50):.0f}")
        col4.metric("Golden Cross", "✓ Yes" if latest.get('golden_cross', False) else "✗ No")
        
        st.markdown("---")
        
        # NAV Chart
        st.subheader("📊 NAV History Chart")
        
        fig = px.line(
            scheme_full_data.tail(100),
            x='date',
            y='net_asset_value',
            title=f"NAV Trend - {selected_scheme_name[:40]} (Last 100 records)",
            labels={'date': 'Date', 'net_asset_value': 'NAV (₹)'},
            markers=True
        )
        
        fig.update_traces(line=dict(color='#1f77b4', width=2))
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Additional Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Returns Distribution")
            
            returns_data = scheme_full_data[['daily_return']].dropna()
            
            fig = px.histogram(
                returns_data,
                x='daily_return',
                nbins=50,
                title="Daily Returns Distribution",
                labels={'daily_return': 'Daily Return %'},
                color_discrete_sequence=['#51CF66']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Moving Averages")
            
            fig = go.Figure()
            
            # Latest 200 records for cleaner chart
            recent = scheme_full_data.tail(200).reset_index(drop=True)
            
            fig.add_trace(go.Scatter(
                x=recent['date'],
                y=recent['net_asset_value'],
                mode='lines',
                name='NAV',
                line=dict(color='#1f77b4', width=1)
            ))
            
            if 'sma_20' in recent.columns:
                fig.add_trace(go.Scatter(
                    x=recent['date'],
                    y=recent['sma_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='#FF6B6B', dash='dash')
                ))
            
            if 'sma_50' in recent.columns:
                fig.add_trace(go.Scatter(
                    x=recent['date'],
                    y=recent['sma_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='#FFD93D', dash='dash')
                ))
            
            fig.update_layout(
                title="NAV with Moving Averages",
                xaxis_title="Date",
                yaxis_title="NAV (₹)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Summary Statistics Table
        st.subheader("📋 Summary Statistics")
        
        summary_stats = {
            'Metric': [
                'Total Records',
                'Date Range',
                'Average NAV',
                'NAV Std Dev',
                'Positive Days %',
                'Negative Days %',
                'Best Day Return',
                'Worst Day Return',
                'Average Daily Return'
            ],
            'Value': [
                len(scheme_full_data),
                f"{scheme_full_data['date'].min().date()} to {scheme_full_data['date'].max().date()}",
                format_currency(scheme_full_data['net_asset_value'].mean()),
                format_currency(scheme_full_data['net_asset_value'].std()),
                f"{(scheme_full_data['daily_return'] > 0).sum() / len(scheme_full_data) * 100:.1f}%",
                f"{(scheme_full_data['daily_return'] < 0).sum() / len(scheme_full_data) * 100:.1f}%",
                format_percent(scheme_full_data['daily_return'].max()),
                format_percent(scheme_full_data['daily_return'].min()),
                format_percent(scheme_full_data['daily_return'].mean())
            ]
        }
        
        st.dataframe(
            pd.DataFrame(summary_stats),
            use_container_width=True,
            hide_index=True
        )
