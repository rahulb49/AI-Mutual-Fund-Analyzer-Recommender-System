"""
Test script for Feature Engineering Module
Demonstrates:
- Moving averages (SMA, EMA)
- Returns and cumulative returns
- Volatility and Sharpe/Sortino ratios
- Maximum drawdown
- Trend analysis
- RSI and trading signals
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingestion.nav_ingestion import fetch_nav_data
from processing.feature_engineering import (
    engineer_features,
    print_feature_summary,
    generate_feature_summary,
    FeatureConfig
)

# Load cleaned data
nav_file = Path(__file__).parent / "data" / "cleaned_nav_data.csv"

print("="*70)
print("FEATURE ENGINEERING TEST - NAV DATA")
print("="*70)

if not nav_file.exists():
    print(f"\n⚠️  Cleaned data not found at {nav_file}")
    print("Using raw data instead...")
    nav_file = Path(__file__).parent / "input" / "NAVAll.txt"
    df, _ = fetch_nav_data(str(nav_file))
else:
    print(f"\n📥 Loading cleaned data from {nav_file}")
    df = pd.read_csv(nav_file)

# Convert date column
df['date'] = pd.to_datetime(df['date'])

print(f"✓ Loaded {len(df):,} records")

# Step 1: Select a sample scheme for detailed analysis
print("\n" + "="*70)
print("📋 Step 1: Selecting Sample Scheme")
print("="*70)

# Get a popular scheme with good history
scheme_sample = df[df['fund_house'] == 'ICICI Prudential Mutual Fund'].tail(100)

if len(scheme_sample) > 0:
    scheme_name = scheme_sample['scheme_name'].iloc[0]
    fund_house = scheme_sample['fund_house'].iloc[0]
    print(f"\nScheme: {scheme_name}")
    print(f"Fund House: {fund_house}")
    print(f"Records: {len(scheme_sample)}")
else:
    print("Could not find suitable scheme, using first available")
    scheme_sample = df.tail(100)
    scheme_name = scheme_sample['scheme_name'].iloc[0]

# Step 2: Engineer features
print("\n" + "="*70)
print("📊 Step 2: Engineering Features")
print("="*70)

config = FeatureConfig(
    ma_short_window=20,
    ma_long_window=50,
    ema_span=12,
    volatility_window=30,
    trend_window=10,
    risk_free_rate=0.06
)

df_features = engineer_features(scheme_sample.copy(), config)

print("\n✓ Features engineered successfully!")
print(f"\nFeatures created:")
features = [col for col in df_features.columns if col not in df.columns]
for i, feat in enumerate(features, 1):
    print(f"  {i:2d}. {feat}")

# Step 3: Display feature summary
print("\n" + "="*70)
print("📈 Step 3: Feature Summary")
print("="*70)

print_feature_summary(df_features, scheme_name)

# Step 4: Show sample records with features
print("\n" + "="*70)
print("📋 Step 4: Sample Records with Features (Last 5)")
print("="*70)

display_cols = [
    'date', 'net_asset_value', 'daily_return', 'cum_return',
    'SMA_20', 'EMA_12', 'volatility_30d', 'sharpe_ratio_30d',
    'max_drawdown_1y', 'trend_slope', 'rsi_14'
]

available_cols = [col for col in display_cols if col in df_features.columns]
last_5 = df_features[available_cols].tail(5).copy()

# Format for display
for col in last_5.columns:
    if col == 'date':
        last_5[col] = last_5[col].dt.strftime('%Y-%m-%d')
    elif col not in ['rsi_14', 'trend_slope', 'trend_strength']:
        if last_5[col].dtype in ['float64', 'float32']:
            last_5[col] = last_5[col].round(4)

print("\n" + last_5.to_string())

# Step 5: Show trend and signal analysis
print("\n" + "="*70)
print("📊 Step 5: Trend & Signal Analysis (Last 10 records)")
print("="*70)

signal_cols = [
    'date', 'net_asset_value', 'daily_return',
    'SMA_20', 'SMA_50', 'EMA_12',
    'golden_cross', 'price_above_ema', 'rsi_overbought', 'rsi_oversold'
]

available_signal_cols = [col for col in signal_cols if col in df_features.columns]
df_signals = df_features[available_signal_cols].tail(10).copy()

# Format signals
df_signals['golden_cross'] = df_signals['golden_cross'].map({0: '✗', 1: '✓'})
df_signals['price_above_ema'] = df_signals['price_above_ema'].map({0: '✗', 1: '✓'})
df_signals['rsi_overbought'] = df_signals['rsi_overbought'].map({0: '✗', 1: '✓'})
df_signals['rsi_oversold'] = df_signals['rsi_oversold'].map({0: '✗', 1: '✓'})

print("\n" + df_signals.to_string(index=False))

# Step 6: Analyze multiple schemes
print("\n" + "="*70)
print("📊 Step 6: Multi-Scheme Comparison")
print("="*70)

# Get schemes from different fund houses
fund_houses = df['fund_house'].unique()[:5]  # Top 5 fund houses
comparison_data = []

for fund in fund_houses:
    fund_data = df[df['fund_house'] == fund].tail(50)
    if len(fund_data) > 10:
        df_feat = engineer_features(fund_data.copy(), config)
        summary = generate_feature_summary(df_feat)
        
        comparison_data.append({
            'Fund House': fund,
            'Scheme': summary.get('scheme_name', 'N/A')[:30],
            'Current NAV': f"₹{summary['nav_metrics']['current_nav']:.2f}",
            'Total Return': f"{summary['returns_metrics']['total_return']:.2f}%",
            'Volatility': f"{summary['risk_metrics']['volatility_30d']:.2f}%",
            'Sharpe Ratio': f"{summary['risk_metrics']['sharpe_ratio_30d']:.2f}",
            'Max Drawdown': f"{summary['risk_metrics']['max_drawdown_1y']:.2f}%"
        })

comparison_df = pd.DataFrame(comparison_data)
print("\n" + comparison_df.to_string(index=False))

# Step 7: Risk categorization
print("\n" + "="*70)
print("⚠️  Step 7: Risk Profile Analysis")
print("="*70)

volatility = df_features['volatility_30d'].iloc[-1]
sharpe = df_features['sharpe_ratio_30d'].iloc[-1]
drawdown = df_features['max_drawdown_1y'].iloc[-1]

print(f"\nVolatility Analysis:")
if volatility < 5:
    print(f"  {volatility:.2f}% → LOW RISK (Conservative fund)")
elif volatility < 15:
    print(f"  {volatility:.2f}% → MODERATE RISK (Balanced fund)")
else:
    print(f"  {volatility:.2f}% → HIGH RISK (Aggressive fund)")

print(f"\nRisk-Adjusted Return (Sharpe Ratio):")
if sharpe > 1:
    print(f"  {sharpe:.2f} → EXCELLENT (Exceptional risk-adjusted returns)")
elif sharpe > 0.5:
    print(f"  {sharpe:.2f} → GOOD (Above-average risk-adjusted returns)")
elif sharpe > 0:
    print(f"  {sharpe:.2f} → FAIR (Positive but modest returns)")
else:
    print(f"  {sharpe:.2f} → POOR (Negative risk-adjusted returns)")

print(f"\nDownside Risk (Max Drawdown):")
if drawdown > -10:
    print(f"  {drawdown:.2f}% → LOW DOWNSIDE RISK")
elif drawdown > -25:
    print(f"  {drawdown:.2f}% → MODERATE DOWNSIDE RISK")
else:
    print(f"  {drawdown:.2f}% → HIGH DOWNSIDE RISK")

# Step 8: Feature correlation
print("\n" + "="*70)
print("🔗 Step 8: Feature Correlation (last 30 days)")
print("="*70)

numeric_features = [
    'net_asset_value', 'daily_return', 'volatility_30d',
    'sharpe_ratio_30d', 'max_drawdown_1y', 'trend_slope', 'rsi_14'
]

available_feat = [col for col in numeric_features if col in df_features.columns]
if len(df_features) >= 30:
    corr = df_features[available_feat].tail(30).corr()
    print("\nCorrelation with Daily Return:")
    daily_ret_corr = corr['daily_return'].drop('daily_return').sort_values(ascending=False)
    for feat, corr_val in daily_ret_corr.items():
        print(f"  {feat:20s}: {corr_val:>7.4f}")

# Save featured data
output_file = Path(__file__).parent / "data" / "nav_with_features.csv"
output_file.parent.mkdir(exist_ok=True)

# Engineer features for all schemes
print("\n" + "="*70)
print("💾 Step 9: Saving All Features")
print("="*70)

all_records = []
for fund_house_group in df.groupby('fund_house'):
    try:
        group_df = fund_house_group[1].tail(50)  # Last 50 records per fund house
        if len(group_df) > 5:
            featured = engineer_features(group_df.copy(), config)
            all_records.append(featured)
    except Exception as e:
        print(f"  ⚠️  Skipping {fund_house_group[0]}: {str(e)[:50]}")

if all_records:
    df_all_features = pd.concat(all_records, ignore_index=True)
    df_all_features.to_csv(output_file, index=False)
    print(f"✓ Saved {len(df_all_features):,} records with features to:")
    print(f"  {output_file}")

print("\n" + "="*70)
print("✓ FEATURE ENGINEERING COMPLETE")
print("="*70)
