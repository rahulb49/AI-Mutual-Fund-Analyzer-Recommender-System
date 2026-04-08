"""
Utility functions for Streamlit Dashboard
"""

import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
from config import FEATURED_DATA, CLEANED_DATA, RISK_LEVELS, SHARPE_LEVELS


@st.cache_resource
def load_featured_data():
    """Load featured data with caching"""
    try:
        df = pd.read_csv(FEATURED_DATA)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading featured data: {e}")
        return None


@st.cache_resource
def load_cleaned_data():
    """Load cleaned data with caching"""
    try:
        df = pd.read_csv(CLEANED_DATA)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading cleaned data: {e}")
        return None


def get_scheme_name(code, df):
    """Get scheme name by code"""
    try:
        scheme = df[df['scheme_code'] == code]
        if len(scheme) > 0:
            return scheme['scheme_name'].iloc[-1]
    except:
        pass
    return f"Scheme {code}"


def categorize_risk(volatility):
    """Categorize risk level based on volatility"""
    if volatility < 5:
        return "🟢 LOW RISK"
    elif volatility < 15:
        return "🟡 MODERATE RISK"
    else:
        return "🔴 HIGH RISK"


def categorize_sharpe(sharpe):
    """Categorize Sharpe ratio performance"""
    if sharpe > 1.0:
        return "⭐⭐⭐⭐⭐ EXCELLENT"
    elif sharpe > 0.5:
        return "⭐⭐⭐⭐ GOOD"
    elif sharpe > 0:
        return "⭐⭐⭐ FAIR"
    else:
        return "⭐⭐ POOR"


def categorize_return(ret):
    """Categorize return performance"""
    if ret > 50:
        return "🌟 Exceptional"
    elif ret > 20:
        return "✨ Very Good"
    elif ret > 0:
        return "✓ Positive"
    else:
        return "✗ Negative"


def format_currency(value):
    """Format currency values"""
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.2f}"


def format_percent(value):
    """Format percentage values"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"


def get_top_schemes(df, metric="sharpe_ratio_30d", limit=10, ascending=False):
    """Get top schemes by metric"""
    try:
        df_unique = df.drop_duplicates('scheme_code', keep='last')
        df_sorted = df_unique.dropna(subset=[metric]).sort_values(
            metric, ascending=ascending
        )
        return df_sorted.head(limit)
    except Exception as e:
        return pd.DataFrame()


def search_schemes(df, query):
    """Search schemes by name or fund house"""
    if not query:
        return df.drop_duplicates('scheme_code', keep='last').head(100)
    
    query_lower = query.lower()
    mask = (
        df['scheme_name'].str.lower().str.contains(query_lower, na=False) |
        df['fund_house'].str.lower().str.contains(query_lower, na=False)
    )
    return df[mask].drop_duplicates('scheme_code', keep='last')


def get_scheme_metrics(df, scheme_code):
    """Get metrics for a specific scheme"""
    scheme_data = df[df['scheme_code'] == scheme_code]
    if len(scheme_data) == 0:
        return None
    
    latest = scheme_data.iloc[-1]
    
    return {
        'scheme_code': int(latest['scheme_code']),
        'scheme_name': latest['scheme_name'],
        'fund_house': latest['fund_house'],
        'current_nav': float(latest['net_asset_value']),
        'nav_min': float(scheme_data['net_asset_value'].min()),
        'nav_max': float(scheme_data['net_asset_value'].max()),
        'avg_nav': float(scheme_data['net_asset_value'].mean()),
        'daily_return': float(latest.get('daily_return', 0)),
        'cum_return': float(latest.get('cum_return', 0)),
        'volatility': float(latest.get('volatility_30d', 0)),
        'sharpe_ratio': float(latest.get('sharpe_ratio_30d', 0)),
        'sortino_ratio': float(latest.get('sortino_ratio_30d', 0)),
        'max_drawdown': float(latest.get('max_drawdown_1y', 0)),
        'trend_direction': latest.get('trend_slope', 0),
        'rsi': float(latest.get('rsi_14', 50)),
        'data_points': len(scheme_data)
    }


def get_fund_house_stats(df):
    """Get statistics by fund house"""
    stats = df.groupby('fund_house').agg({
        'scheme_code': 'nunique',
        'net_asset_value': ['min', 'max', 'mean'],
        'volatility_30d': 'mean',
        'sharpe_ratio_30d': 'mean'
    }).round(2)
    
    stats.columns = ['schemes', 'min_nav', 'max_nav', 'avg_nav', 'avg_volatility', 'avg_sharpe']
    stats = stats.sort_values('schemes', ascending=False)
    return stats


def get_market_stats(df):
    """Get overall market statistics"""
    return {
        'total_schemes': df['scheme_code'].nunique(),
        'total_records': len(df),
        'fund_houses': df['fund_house'].nunique(),
        'date_range_start': df['date'].min(),
        'date_range_end': df['date'].max(),
        'avg_nav': df['net_asset_value'].mean(),
        'min_nav': df['net_asset_value'].min(),
        'max_nav': df['net_asset_value'].max(),
        'avg_volatility': df['volatility_30d'].mean() if 'volatility_30d' in df.columns else 0,
        'avg_sharpe': df['sharpe_ratio_30d'].mean() if 'sharpe_ratio_30d' in df.columns else 0,
    }


def setup_page_style():
    """Setup Streamlit page styling"""
    st.set_page_config(
        page_title="NAV Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .highlight {
            background-color: #fffacd;
            padding: 5px 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_metric_card(title, value, subtitle="", col=None):
    """Render a metric card"""
    if col is None:
        st.metric(title, value, subtitle)
    else:
        col.metric(title, value, subtitle)
