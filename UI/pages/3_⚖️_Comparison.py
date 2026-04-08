"""
Scheme Comparison Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    load_featured_data, format_currency, format_percent, setup_page_style
)

setup_page_style()

st.title("⚖️ Scheme Comparison")
st.markdown("*Compare multiple schemes side by side*")

# Load data
@st.cache_resource
def init_data():
    return load_featured_data()

featured_df = init_data()

if featured_df is None:
    st.error("❌ Failed to load data")
    st.stop()

# Get unique schemes
schemes_list = featured_df.drop_duplicates(
    'scheme_code', keep='last'
).sort_values('scheme_name')['scheme_name'].values

# Multi-select schemes
st.subheader("📋 Select Schemes to Compare")

selected_schemes = st.multiselect(
    "Choose 2-5 schemes:",
    schemes_list,
    max_selections=5,
    key="compare_select"
)

if len(selected_schemes) < 2:
    st.info("📌 Select at least 2 schemes to start comparing")
else:
    # Prepare comparison data
    comparison_data = []
    scheme_histories = {}
    
    for scheme in selected_schemes:
        scheme_code = featured_df[featured_df['scheme_name'] == scheme]['scheme_code'].iloc[0]
        scheme_latest = featured_df[featured_df['scheme_code'] == scheme_code].sort_values('date').iloc[-1]
        scheme_history = featured_df[featured_df['scheme_code'] == scheme_code].sort_values('date')
        
        scheme_histories[scheme] = scheme_history
        
        comparison_data.append({
            'Scheme': scheme,
            'Fund House': scheme_latest['fund_house'],
            'Current NAV': float(scheme_latest['net_asset_value']),
            'Avg NAV': float(scheme_history['net_asset_value'].mean()),
            'Return %': float(scheme_latest.get('cum_return', 0)),
            'Daily Return %': float(scheme_latest.get('daily_return', 0)),
            'Volatility %': float(scheme_latest.get('volatility_30d', 0)),
            'Sharpe Ratio': float(scheme_latest.get('sharpe_ratio_30d', 0)),
            'Sortino Ratio': float(scheme_latest.get('sortino_ratio_30d', 0)),
            'Max Drawdown %': float(scheme_latest.get('max_drawdown_1y', 0)),
            'Data Points': len(scheme_history)
        })
    
    comp_df = pd.DataFrame(comparison_data)
    
    st.markdown("---")
    
    # Display comparison table
    st.subheader("📊 Detailed Comparison")
    
    display_cols = ['Scheme', 'Fund House', 'Current NAV', 'Return %', 'Volatility %', 'Sharpe Ratio']
    
    st.dataframe(
        comp_df[display_cols],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Charts
    st.subheader("📈 Visual Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Return vs Volatility
        fig = px.scatter(
            comp_df,
            x='Volatility %',
            y='Return %',
            size='Sharpe Ratio',
            hover_name='Scheme',
            hover_data=['Fund House', 'Sharpe Ratio'],
            title="Return vs Risk (Size = Sharpe Ratio)",
            color='Sharpe Ratio',
            color_continuous_scale='RdYlGn',
            size_max=500
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sharpe Ratio Comparison
        fig = px.bar(
            comp_df.sort_values('Sharpe Ratio', ascending=True),
            x='Sharpe Ratio',
            y='Scheme',
            orientation='h',
            title="Sharpe Ratio Comparison",
            color='Sharpe Ratio',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volatility Comparison
        fig = px.bar(
            comp_df.sort_values('Volatility %', ascending=False),
            x='Volatility %',
            y='Scheme',
            orientation='h',
            title="Risk (Volatility) Comparison",
            color='Volatility %',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Return Comparison
        fig = px.bar(
            comp_df.sort_values('Return %', ascending=True),
            x='Return %',
            y='Scheme',
            orientation='h',
            title="Cumulative Return Comparison",
            color='Return %',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # NAV History Comparison
    st.subheader("📉 NAV Trend Comparison")
    
    fig = go.Figure()
    
    for scheme in selected_schemes:
        scheme_history = scheme_histories[scheme].tail(100)
        
        fig.add_trace(go.Scatter(
            x=scheme_history['date'],
            y=scheme_history['net_asset_value'],
            mode='lines',
            name=scheme[:30],
            line=dict(width=2.5)
        ))
    
    fig.update_layout(
        title="NAV Trends Over Time (Last 100 records)",
        xaxis_title="Date",
        yaxis_title="NAV (₹)",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Performance Summary
    st.subheader("🏆 Selection Guidance")
    
    col1, col2, col3 = st.columns(3)
    
    # Best Return
    best_return = comp_df.loc[comp_df['Return %'].idxmax()]
    col1.metric(
        "Best Return",
        best_return['Scheme'][:25],
        f"{best_return['Return %']:.2f}%"
    )
    
    # Best Risk-Adjusted Return
    best_sharpe = comp_df.loc[comp_df['Sharpe Ratio'].idxmax()]
    col2.metric(
        "Best Risk-Adjusted",
        best_sharpe['Scheme'][:25],
        f"{best_sharpe['Sharpe Ratio']:.2f}"
    )
    
    # Lowest Risk
    lowest_risk = comp_df.loc[comp_df['Volatility %'].idxmin()]
    col3.metric(
        "Lowest Risk",
        lowest_risk['Scheme'][:25],
        f"{lowest_risk['Volatility %']:.2f}%"
    )
    
    st.markdown("---")
    
    # Detailed Metrics Table
    st.subheader("📋 Full Metrics Table")
    
    full_display = comp_df[[
        'Scheme', 'Fund House', 'Current NAV', 'Avg NAV',
        'Return %', 'Volatility %', 'Sharpe Ratio', 'Sortino Ratio',
        'Max Drawdown %', 'Data Points'
    ]].copy()
    
    # Format numeric columns
    for col in ['Current NAV', 'Avg NAV']:
        full_display[col] = full_display[col].apply(lambda x: f"₹{x:.2f}")
    
    for col in ['Return %', 'Volatility %', 'Max Drawdown %']:
        full_display[col] = full_display[col].apply(lambda x: f"{x:.2f}%")
    
    for col in ['Sharpe Ratio', 'Sortino Ratio']:
        full_display[col] = full_display[col].apply(lambda x: f"{x:.3f}")
    
    st.dataframe(
        full_display,
        use_container_width=True,
        hide_index=True
    )
