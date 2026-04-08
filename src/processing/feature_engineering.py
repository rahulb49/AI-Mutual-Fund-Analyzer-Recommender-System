"""
Feature Engineering Module for NAV Data
Generates financial features and metrics:
- Moving averages (Simple, Exponential)
- Trend analysis (direction, strength, slope)
- Risk metrics (volatility, Sharpe ratio, Sortino ratio, max drawdown)
- Performance metrics (returns, cumulative returns)
- Scheme classification
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class FeatureConfig:
    """Configuration for feature engineering"""
    ma_short_window: int = 20      # Short moving average window (days)
    ma_long_window: int = 50       # Long moving average window (days)
    ema_span: int = 12             # EMA span parameter
    volatility_window: int = 30    # Volatility calculation window
    trend_window: int = 10         # Trend analysis window
    risk_free_rate: float = 0.06   # Annual risk-free rate (6%)
    
    def get_risk_free_daily(self) -> float:
        """Convert annual risk-free rate to daily"""
        return self.risk_free_rate / 252


def calculate_simple_moving_average(series: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        series: Price series
        window: Window size
        
    Returns:
        SMA series
    """
    return series.rolling(window=window, min_periods=1).mean()


def calculate_exponential_moving_average(series: pd.Series, span: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    More weight to recent prices.
    
    Args:
        series: Price series
        span: Span parameter (equivalent to window)
        
    Returns:
        EMA series
    """
    return series.ewm(span=span, adjust=False).mean()


def calculate_returns(nav_series: pd.Series, periods: int = 1) -> pd.Series:
    """
    Calculate percentage returns.
    
    Args:
        nav_series: NAV series
        periods: Number of periods for return calculation
        
    Returns:
        Returns series (in percentage)
    """
    return nav_series.pct_change(periods=periods) * 100


def calculate_cumulative_returns(nav_series: pd.Series) -> pd.Series:
    """
    Calculate cumulative returns from start.
    
    Args:
        nav_series: NAV series
        
    Returns:
        Cumulative returns (in percentage)
    """
    if len(nav_series) == 0:
        return pd.Series()
    
    first_value = nav_series.iloc[0]
    return ((nav_series - first_value) / first_value) * 100


def calculate_volatility(returns: pd.Series, window: int = 30, annualized: bool = True) -> pd.Series:
    """
    Calculate volatility (standard deviation of returns).
    
    Args:
        returns: Returns series (in percentage)
        window: Rolling window size
        annualized: If True, annualize the volatility
        
    Returns:
        Volatility series
    """
    volatility = returns.rolling(window=window, min_periods=1).std()
    
    if annualized:
        # Annualize: daily volatility * sqrt(252 trading days)
        volatility = volatility * np.sqrt(252)
    
    return volatility


def calculate_sharpe_ratio(returns: pd.Series, window: int = 30, risk_free_rate: float = 0.06) -> pd.Series:
    """
    Calculate Sharpe Ratio - reward per unit of risk.
    
    Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
    
    Args:
        returns: Daily returns (in decimal, not percentage)
        window: Rolling window size
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Sharpe ratio series
    """
    risk_free_daily = risk_free_rate / 252
    
    # Calculate rolling mean return and volatility
    mean_return = returns.rolling(window=window, min_periods=1).mean()
    volatility = returns.rolling(window=window, min_periods=1).std()
    
    # Avoid division by zero
    sharpe = np.where(
        volatility != 0,
        (mean_return - risk_free_daily) / volatility * np.sqrt(252),
        0
    )
    
    return pd.Series(sharpe, index=returns.index)


def calculate_sortino_ratio(returns: pd.Series, window: int = 30, 
                            risk_free_rate: float = 0.06, target_return: float = 0.0) -> pd.Series:
    """
    Calculate Sortino Ratio - penalizes only downside volatility.
    
    Sortino Ratio = (Return - Target) / Downside Deviation
    
    Args:
        returns: Daily returns (in decimal)
        window: Rolling window size
        risk_free_rate: Annual risk-free rate
        target_return: Target return (daily)
        
    Returns:
        Sortino ratio series
    """
    risk_free_daily = risk_free_rate / 252
    
    mean_return = returns.rolling(window=window, min_periods=1).mean()
    
    # Calculate downside deviation (only negative returns)
    downside_returns = returns.copy()
    downside_returns[downside_returns > target_return] = 0
    downside_deviation = downside_returns.rolling(window=window, min_periods=1).std()
    
    sortino = np.where(
        downside_deviation != 0,
        (mean_return - risk_free_daily) / downside_deviation * np.sqrt(252),
        0
    )
    
    return pd.Series(sortino, index=returns.index)


def calculate_max_drawdown(nav_series: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate Maximum Drawdown - largest peak-to-trough decline.
    
    Args:
        nav_series: NAV price series
        window: Rolling window size (default 252 = 1 year)
        
    Returns:
        Maximum drawdown series (in percentage)
    """
    running_max = nav_series.rolling(window=window, min_periods=1).max()
    drawdown = (nav_series - running_max) / running_max * 100
    
    return drawdown


def calculate_trend_strength(nav_series: pd.Series, window: int = 10) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate trend strength using linear regression slope.
    
    Args:
        nav_series: NAV series
        window: Window for trend calculation
        
    Returns:
        Tuple of (trend_slope, trend_strength)
        - trend_slope: Steepness of trend
        - trend_strength: R² value (0-1, higher means stronger trend)
    """
    x = np.arange(window)
    slopes = []
    r_squared = []
    
    for i in range(len(nav_series) - window + 1):
        y = nav_series.iloc[i:i+window].values
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        slopes.append(slope)
        
        # R² value
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        r_squared.append(r2)
    
    # Pad the beginning with NaN
    trend_slope = pd.Series(
        [np.nan] * (window - 1) + slopes,
        index=nav_series.index
    )
    trend_strength = pd.Series(
        [np.nan] * (window - 1) + r_squared,
        index=nav_series.index
    )
    
    return trend_slope, trend_strength


def calculate_rsi(returns: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Momentum indicator: 0-100 scale (>70 overbought, <30 oversold)
    
    Args:
        returns: Returns series (in decimal)
        window: Window size
        
    Returns:
        RSI series
    """
    # Calculate gains and losses
    delta = returns.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
    
    # Avoid division by zero
    rs = np.where(loss != 0, gain / loss, 0)
    rsi = 100 - (100 / (1 + rs))
    
    return pd.Series(rsi, index=returns.index)


def categorize_scheme_performance(nav_series: pd.Series, returns: pd.Series) -> Dict[str, str]:
    """
    Categorize scheme performance over different periods.
    
    Args:
        nav_series: NAV series
        returns: Returns series
        
    Returns:
        Dictionary with performance categories
    """
    if len(nav_series) < 2:
        return {'status': 'insufficient_data'}
    
    # Latest return
    latest_return = returns.iloc[-1]
    
    # Category based on performance
    categories = {}
    
    if latest_return > 10:
        categories['short_term'] = 'Strong Positive'
    elif latest_return > 0:
        categories['short_term'] = 'Positive'
    elif latest_return > -5:
        categories['short_term'] = 'Neutral'
    else:
        categories['short_term'] = 'Negative'
    
    # Trend direction
    trend_slope, _ = calculate_trend_strength(nav_series, window=10)
    if not trend_slope.iloc[-1:].isna().any():
        if trend_slope.iloc[-1] > 0:
            categories['trend'] = 'Uptrend'
        elif trend_slope.iloc[-1] < 0:
            categories['trend'] = 'Downtrend'
        else:
            categories['trend'] = 'Neutral'
    
    return categories


def engineer_features(df: pd.DataFrame, config: Optional[FeatureConfig] = None) -> pd.DataFrame:
    """
    Comprehensive feature engineering pipeline.
    
    Creates all features:
    - Moving averages (SMA, EMA)
    - Returns (daily, cumulative)
    - Volatility metrics
    - Risk metrics (Sharpe, Sortino, Max Drawdown)
    - Trend analysis
    - RSI
    
    Args:
        df: DataFrame with NAV data (must have 'net_asset_value' column)
        config: FeatureConfig object (uses defaults if None)
        
    Returns:
        DataFrame with engineered features
    """
    if config is None:
        config = FeatureConfig()
    
    df = df.copy()
    
    # Sort by date to ensure proper time series calculations
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
    
    # ===== Moving Averages =====
    df['SMA_20'] = calculate_simple_moving_average(df['net_asset_value'], config.ma_short_window)
    df['SMA_50'] = calculate_simple_moving_average(df['net_asset_value'], config.ma_long_window)
    df['EMA_12'] = calculate_exponential_moving_average(df['net_asset_value'], config.ema_span)
    
    # ===== Returns =====
    df['daily_return'] = calculate_returns(df['net_asset_value'], periods=1)
    df['daily_return_decimal'] = df['daily_return'] / 100  # Convert to decimal
    df['cum_return'] = calculate_cumulative_returns(df['net_asset_value'])
    
    # ===== Volatility =====
    df['volatility_30d'] = calculate_volatility(
        df['daily_return'],
        window=config.volatility_window,
        annualized=True
    )
    
    # ===== Risk Metrics =====
    df['sharpe_ratio_30d'] = calculate_sharpe_ratio(
        df['daily_return_decimal'],
        window=config.volatility_window,
        risk_free_rate=config.risk_free_rate
    )
    
    df['sortino_ratio_30d'] = calculate_sortino_ratio(
        df['daily_return_decimal'],
        window=config.volatility_window,
        risk_free_rate=config.risk_free_rate
    )
    
    df['max_drawdown_1y'] = calculate_max_drawdown(df['net_asset_value'], window=252)
    
    # ===== Trend Analysis =====
    trend_slope, trend_strength = calculate_trend_strength(
        df['net_asset_value'],
        window=config.trend_window
    )
    df['trend_slope'] = trend_slope
    df['trend_strength'] = trend_strength
    
    # ===== RSI =====
    df['rsi_14'] = calculate_rsi(df['daily_return_decimal'], window=14)
    
    # ===== Signal Lines =====
    # Golden Cross: SMA_20 > SMA_50 (bullish)
    df['golden_cross'] = (df['SMA_20'] > df['SMA_50']).astype(int)
    
    # Price above/below EMA
    df['price_above_ema'] = (df['net_asset_value'] > df['EMA_12']).astype(int)
    
    # RSI Signals
    df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
    df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
    
    return df


def generate_feature_summary(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics of engineered features.
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': str(df['date'].min()) if 'date' in df.columns else 'N/A',
            'end': str(df['date'].max()) if 'date' in df.columns else 'N/A'
        },
        'nav_metrics': {
            'current_nav': float(df['net_asset_value'].iloc[-1]),
            'avg_nav': float(df['net_asset_value'].mean()),
            'nav_min': float(df['net_asset_value'].min()),
            'nav_max': float(df['net_asset_value'].max())
        },
        'returns_metrics': {
            'total_return': float(df['cum_return'].iloc[-1]) if len(df) > 0 else 0,
            'avg_daily_return': float(df['daily_return'].mean()),
            'best_day': float(df['daily_return'].max()),
            'worst_day': float(df['daily_return'].min())
        },
        'risk_metrics': {
            'volatility_30d': float(df['volatility_30d'].iloc[-1]) if not df['volatility_30d'].iloc[-1:].isna().any() else 0,
            'sharpe_ratio_30d': float(df['sharpe_ratio_30d'].iloc[-1]) if not df['sharpe_ratio_30d'].iloc[-1:].isna().any() else 0,
            'sortino_ratio_30d': float(df['sortino_ratio_30d'].iloc[-1]) if not df['sortino_ratio_30d'].iloc[-1:].isna().any() else 0,
            'max_drawdown_1y': float(df['max_drawdown_1y'].iloc[-1]) if not df['max_drawdown_1y'].iloc[-1:].isna().any() else 0
        },
        'trend_metrics': {
            'current_trend_slope': float(df['trend_slope'].iloc[-1]) if not df['trend_slope'].iloc[-1:].isna().any() else 0,
            'trend_strength': float(df['trend_strength'].iloc[-1]) if not df['trend_strength'].iloc[-1:].isna().any() else 0,
            'golden_cross': bool(df['golden_cross'].iloc[-1]) if len(df) > 0 else False,
            'price_above_ema': bool(df['price_above_ema'].iloc[-1]) if len(df) > 0 else False
        }
    }
    
    return summary


def print_feature_summary(df: pd.DataFrame, scheme_name: str = "NAV Scheme"):
    """Pretty print feature summary."""
    summary = generate_feature_summary(df)
    
    print(f"\n{'='*70}")
    print(f"FEATURE SUMMARY: {scheme_name}")
    print(f"{'='*70}")
    
    print(f"\n📅 Time Period:")
    print(f"  {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"  Records: {summary['total_records']:,}")
    
    print(f"\n💰 NAV Metrics:")
    print(f"  Current NAV:       ₹{summary['nav_metrics']['current_nav']:>12.4f}")
    print(f"  Average NAV:       ₹{summary['nav_metrics']['avg_nav']:>12.4f}")
    print(f"  Min NAV:           ₹{summary['nav_metrics']['nav_min']:>12.4f}")
    print(f"  Max NAV:           ₹{summary['nav_metrics']['nav_max']:>12.4f}")
    
    print(f"\n📈 Returns:")
    print(f"  Total Return:      {summary['returns_metrics']['total_return']:>12.2f}%")
    print(f"  Avg Daily Return:  {summary['returns_metrics']['avg_daily_return']:>12.4f}%")
    print(f"  Best Day:          {summary['returns_metrics']['best_day']:>12.4f}%")
    print(f"  Worst Day:         {summary['returns_metrics']['worst_day']:>12.4f}%")
    
    print(f"\n⚠️  Risk Metrics:")
    print(f"  Volatility (30d):  {summary['risk_metrics']['volatility_30d']:>12.2f}%")
    print(f"  Sharpe Ratio:      {summary['risk_metrics']['sharpe_ratio_30d']:>12.2f}")
    print(f"  Sortino Ratio:     {summary['risk_metrics']['sortino_ratio_30d']:>12.2f}")
    print(f"  Max Drawdown (1y): {summary['risk_metrics']['max_drawdown_1y']:>12.2f}%")
    
    print(f"\n📊 Trend Analysis:")
    print(f"  Trend Slope:       {summary['trend_metrics']['current_trend_slope']:>12.6f}")
    print(f"  Trend Strength:    {summary['trend_metrics']['trend_strength']:>12.2f} (R²)")
    print(f"  Golden Cross:      {'✓ Yes' if summary['trend_metrics']['golden_cross'] else '✗ No':>12}")
    print(f"  Price > EMA:       {'✓ Yes' if summary['trend_metrics']['price_above_ema'] else '✗ No':>12}")
    
    print(f"{'='*70}\n")
