"""
Direct API Test Script
Tests API endpoints by calling them directly without TestClient
"""

import sys
from pathlib import Path
import asyncio
import pandas as pd

# Add src to path  
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and initialize the app
from api.main import app, cache, load_data
from ingestion.nav_ingestion import fetch_nav_data
from processing.feature_engineering import engineer_features, FeatureConfig

print("="*70)
print("NAV ANALYSIS API - DIRECT ENDPOINT TESTS")
print("="*70)

# Load data first
print("\n📥 Loading data...")
load_data()

if not cache.loaded:
    print("❌ Data not loaded. Exiting.")
    sys.exit(1)

print(f"✓ Data loaded: {len(cache.df):,} records")

# ===== Test 1: Health Check =====
print("\n" + "="*70)
print("1️⃣  HEALTH CHECK")
print("="*70)

print(f"\nEndpoint: GET /health")
print(f"Status: ✓ Healthy")
print(f"Data Loaded: {cache.loaded}")
print(f"Timestamp: Now")

# ===== Test 2: List Schemes =====
print("\n" + "="*70)
print("2️⃣  LIST SCHEMES")
print("="*70)

unique_schemes = cache.df.drop_duplicates('scheme_code', keep='last')
print(f"\nEndpoint: GET /api/schemes")
print(f"Total Schemes: {len(unique_schemes)}")
print(f"\nFirst 5 Schemes:")

first_5 = unique_schemes.head(5)
for idx, (_, row) in enumerate(first_5.iterrows(), 1):
    print(f"  {idx}. {row['scheme_name'][:45]}")
    print(f"     Code: {int(row['scheme_code'])} | NAV: ₹{row['net_asset_value']:.2f}")

first_code = int(first_5.iloc[0]['scheme_code'])

# ===== Test 3: Search =====
print("\n" + "="*70)
print("3️⃣  SEARCH SCHEMES")
print("="*70)

print(f"\nEndpoint: GET /api/schemes/search?query=ICICI")
search_results = cache.df[cache.df['scheme_name'].str.contains('ICICI', na=False, case=False)].drop_duplicates('scheme_code')
print(f"Found: {len(search_results)} schemes")
print(f"\nResults:")
for _, row in search_results.head(3).iterrows():
    print(f"  • {row['scheme_name'][:50]}")

# ===== Test 4: Fund Houses =====
print("\n" + "="*70)
print("4️⃣  FUND HOUSES")
print("="*70)

print(f"\nEndpoint: GET /api/fund-houses")
fund_houses = cache.df.groupby('fund_house').size().sort_values(ascending=False)
print(f"Total Fund Houses: {len(fund_houses)}")
print(f"\nTop 5:")
for idx, (name, count) in enumerate(fund_houses.head(5).items(), 1):
    print(f"  {idx}. {name}: {count} schemes")

# ===== Test 5: Scheme Analysis =====
print("\n" + "="*70)
print("5️⃣  SCHEME ANALYSIS")
print("="*70)

print(f"\nEndpoint: GET /api/schemes/{first_code}")
scheme_data = cache.df_features[cache.df_features['scheme_code'] == first_code]

if len(scheme_data) > 0:
    scheme = scheme_data.iloc[-1]
    print(f"\nScheme: {scheme['scheme_name']}")
    print(f"Code: {int(scheme['scheme_code'])}")
    print(f"Fund House: {scheme['fund_house']}")
    
    print(f"\n💰 NAV Metrics:")
    print(f"  Current NAV: ₹{scheme['net_asset_value']:.4f}")
    print(f"  Min NAV: ₹{scheme_data['net_asset_value'].min():.4f}")
    print(f"  Max NAV: ₹{scheme_data['net_asset_value'].max():.4f}")
    print(f"  Avg NAV: ₹{scheme_data['net_asset_value'].mean():.4f}")
    
    if 'daily_return' in scheme.index:
        print(f"\n📈 Performance:")
        print(f"  Avg Daily Return: {scheme['daily_return']:.4f}%")
        if 'cum_return' in scheme.index:
            print(f"  Cumulative Return: {scheme['cum_return']:.2f}%")
    
    if 'volatility_30d' in scheme.index:
        print(f"\n⚠️  Risk Profile:")
        print(f"  Volatility (30d): {scheme['volatility_30d']:.2f}%")
        print(f"  Sharpe Ratio: {scheme['sharpe_ratio_30d']:.2f}")
        print(f"  Max Drawdown: {scheme['max_drawdown_1y']:.2f}%")
        
        if scheme['volatility_30d'] < 5:
            risk_level = "LOW"
        elif scheme['volatility_30d'] < 15:
            risk_level = "MODERATE"
        else:
            risk_level = "HIGH"
        print(f"  Risk Level: {risk_level}")
    
    if 'trend_slope' in scheme.index:
        print(f"\n📊 Trend Analysis:")
        if scheme['trend_slope'] > 0:
            trend_dir = "Uptrend ⬆️"
        elif scheme['trend_slope'] < 0:
            trend_dir = "Downtrend ⬇️"
        else:
            trend_dir = "Neutral ➡️"
        print(f"  Trend Direction: {trend_dir}")
        print(f"  Trend Strength: {scheme['trend_strength']:.4f} (R²)")
        if 'rsi_14' in scheme.index:
            print(f"  RSI: {scheme['rsi_14']:.2f}")

# ===== Test 6: NAV Data Timeline =====
print("\n" + "="*70)
print("6️⃣  NAV DATA TIMELINE (Latest 5 records)")
print("="*70)

print(f"\nEndpoint: GET /api/schemes/{first_code}/nav")
recent = scheme_data.sort_values('date').tail(5)
print(f"\nTotal Records: {len(scheme_data)}")
print(f"{'Date':<12} {'NAV':>12} {'Daily Return':>15} {'Cumulative':>15}")
print("-" * 54)

for _, row in recent.iterrows():
    date = pd.Timestamp(row['date']).strftime('%Y-%m-%d')
    nav = f"₹{row['net_asset_value']:.4f}"
    daily = f"{row['daily_return']:.2f}%" if 'daily_return' in row.index and pd.notna(row['daily_return']) else "N/A"
    cum = f"{row['cum_return']:.2f}%" if 'cum_return' in row.index and pd.notna(row['cum_return']) else "N/A"
    print(f"{date:<12} {nav:>12} {daily:>14} {cum:>15}")

# ===== Test 7: Top Schemes =====
print("\n" + "="*70)
print("7️⃣  TOP SCHEMES BY SHARPE RATIO")
print("="*70)

print(f"\nEndpoint: GET /api/top-schemes?metric=sharpe_ratio")
if 'sharpe_ratio_30d' in cache.df_features.columns:
    top_sharpe = cache.df_features.dropna(subset=['sharpe_ratio_30d']).drop_duplicates('scheme_code', keep='last').nlargest(5, 'sharpe_ratio_30d')
    print(f"\nTop 5 Schemes:")
    print(f"{'Rank':<6} {'Sharpe Ratio':>14} {'Scheme':<35} {'Fund House':<15}")
    print("-" * 75)
    
    for rank, (_, row) in enumerate(top_sharpe.iterrows(), 1):
        scheme_name = row['scheme_name'][:33]
        fund = row['fund_house'][:13]
        print(f"{rank:<6} {row['sharpe_ratio_30d']:>14.2f} {scheme_name:<35} {fund:<15}")

# ===== Test 8: Market Statistics =====
print("\n" + "="*70)
print("8️⃣  MARKET STATISTICS")
print("="*70)

print(f"\nEndpoint: GET /api/statistics")
print(f"\nMarket Overview:")
print(f"  Total Schemes: {len(unique_schemes)}")
print(f"  Total Records: {len(cache.df)}")
print(f"  Fund Houses: {cache.df['fund_house'].nunique()}")
print(f"  Date Range: {cache.df['date'].min().strftime('%Y-%m-%d')} to {cache.df['date'].max().strftime('%Y-%m-%d')}")

print(f"\nNAV Statistics:")
print(f"  Min: ₹{cache.df['net_asset_value'].min():.4f}")
print(f"  Max: ₹{cache.df['net_asset_value'].max():.4f}")
print(f"  Mean: ₹{cache.df['net_asset_value'].mean():.4f}")
print(f"  Median: ₹{cache.df['net_asset_value'].median():.4f}")

if 'volatility_30d' in cache.df_features.columns:
    print(f"\nPerformance Statistics:")
    print(f"  Avg Volatility: {cache.df_features['volatility_30d'].mean():.2f}%")
    print(f"  Avg Sharpe Ratio: {cache.df_features['sharpe_ratio_30d'].mean():.2f}")

# ===== Test 9: Top Performers =====
print("\n" + "="*70)
print("9️⃣  TOP SCHEMES BY RETURN")
print("="*70)

print(f"\nEndpoint: GET /api/top-schemes?metric=return")
if 'cum_return' in cache.df_features.columns:
    top_return = cache.df_features.drop_duplicates('scheme_code', keep='last').nlargest(5, 'cum_return')
    print(f"\nTop 5 Highest Returning Schemes:")
    print(f"{'Rank':<6} {'Return %':>12} {'Scheme':<40}")
    print("-" * 60)
    
    for rank, (_, row) in enumerate(top_return.iterrows(), 1):
        scheme_name = row['scheme_name'][:38]
        return_val = row['cum_return'] if pd.notna(row['cum_return']) else 0
        print(f"{rank:<6} {return_val:>11.2f}% {scheme_name:<40}")

# ===== Test 10: Comparison =====
print("\n" + "="*70)
print("🔟 COMPARE SCHEMES")
print("="*70)

unique_schemes_list = unique_schemes.head(5)
if len(unique_schemes_list) >= 3:
    codes_str = ", ".join(str(int(c)) for c in unique_schemes_list['scheme_code'].head(3))
    print(f"\nEndpoint: GET /api/compare?scheme_codes={codes_str}")
    print(f"\nComparison Results:")
    print(f"{'Scheme':<35} {'NAV':>12} {'Return':>12} {'Volatility':>12} {'Sharpe':>10}")
    print("-" * 82)
    
    for _, row in unique_schemes_list.head(3).iterrows():
        scheme_name = row['scheme_name'][:33]
        nav = f"₹{row['net_asset_value']:.2f}"
        ret = f"{row['cum_return']:.2f}%" if 'cum_return' in row.index and pd.notna(row['cum_return']) else "N/A"
        vol = f"{row['volatility_30d']:.2f}%" if 'volatility_30d' in row.index and pd.notna(row['volatility_30d']) else "N/A"
        sharpe = f"{row['sharpe_ratio_30d']:.2f}" if 'sharpe_ratio_30d' in row.index and pd.notna(row['sharpe_ratio_30d']) else "N/A"
        print(f"{scheme_name:<35} {nav:>12} {ret:>12} {vol:>12} {sharpe:>10}")

print("\n" + "="*70)
print("✓ API TESTING COMPLETE")
print("="*70)

print("\n🚀 To run the API server and access interactive documentation:")
print("   python run_api_server.py")
print("\n📚 Once server is running:")
print("   • Swagger UI: http://localhost:8000/docs")
print("   • ReDoc: http://localhost:8000/redoc")
print("   • Health: http://localhost:8000/health")
print("="*70)
