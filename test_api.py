"""
API Test Script
Tests all endpoints without running the server
Uses FastAPI's TestClient
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from fastapi.testclient import TestClient
except Exception as e:
    print(f"⚠️  TestClient import failed: {e}")
    print("Trying with httpx...")
    import httpx
    class TestClient:
        def __init__(self, app):
            from starlette.testclient import TestClient as StarletteTestClient
            self.client = StarletteTestClient(app)
        def get(self, url, **kwargs):
            return self.client.get(url, **kwargs)

from api.main import app

try:
    client = TestClient(app)
except Exception as e:
    print(f"Error creating TestClient: {e}")
    print("Using alternative approach...")
    from starlette.testclient import TestClient as StarletteTestClient
    client = StarletteTestClient(app)

print("="*70)
print("NAV ANALYSIS API - ENDPOINT TESTS")
print("="*70)

# ===== Test 1: Health Check =====
print("\n" + "="*70)
print("1️⃣  HEALTH CHECK")
print("="*70)

response = client.get("/health")
print(f"\nGET /health")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
print(f"Data Loaded: {result['data_loaded']}")

if not result['data_loaded']:
    print("\n⚠️  Data not loaded. Loading...")
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from api.main import load_data
    load_data()

# ===== Test 2: List Schemes =====
print("\n" + "="*70)
print("2️⃣  LIST ALL SCHEMES (with pagination)")
print("="*70)

response = client.get("/api/schemes?limit=5&offset=0")
print(f"\nGET /api/schemes?limit=5&offset=0")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total Schemes: {result['total']}")
print(f"Returned: {result['returned']}")
print(f"\nFirst 5 Schemes:")
for scheme in result['schemes']:
    print(f"  • {scheme['scheme_name']} | NAV: ₹{scheme['current_nav']:.2f}")

# Get a scheme code for other tests
first_scheme_code = result['schemes'][0]['scheme_code'] if result['schemes'] else None

# ===== Test 3: Search Schemes =====
print("\n" + "="*70)
print("3️⃣  SEARCH SCHEMES")
print("="*70)

response = client.get("/api/schemes/search?query=ICICI&limit=5")
print(f"\nGET /api/schemes/search?query=ICICI&limit=5")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total Found: {result['total_found']}")
print(f"Query: {result['query']}")
if result['schemes']:
    print(f"\nResults:")
    for scheme in result['schemes'][:3]:
        print(f"  • {scheme['scheme_name']}")

# ===== Test 4: Fund Houses =====
print("\n" + "="*70)
print("4️⃣  LIST FUND HOUSES")
print("="*70)

response = client.get("/api/fund-houses")
print(f"\nGET /api/fund-houses")
print(f"Status: {response.status_code}")
result = response.json()
print(f"Total Fund Houses: {result['total_fund_houses']}")
print(f"\nTop 5 Fund Houses:")
for house in result['fund_houses'][:5]:
    print(f"  • {house['fund_house']}")
    print(f"    Schemes: {house['scheme_count']}, Avg NAV: ₹{house['avg_nav']:.2f}")

# ===== Test 5: Get Scheme Analysis =====
if first_scheme_code:
    print("\n" + "="*70)
    print("5️⃣  GET SCHEME ANALYSIS (Complete)")
    print("="*70)
    
    response = client.get(f"/api/schemes/{first_scheme_code}")
    print(f"\nGET /api/schemes/{first_scheme_code}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nScheme: {result['scheme_name']}")
        print(f"Fund House: {result['fund_house']}")
        print(f"Data Points: {result['data_points']}")
        
        print(f"\n💰 NAV Metrics:")
        nav = result['nav_metrics']
        print(f"  Current NAV: ₹{nav['current_nav']:.4f}")
        print(f"  Min NAV: ₹{nav['nav_min']:.4f}")
        print(f"  Max NAV: ₹{nav['nav_max']:.4f}")
        print(f"  Avg NAV: ₹{nav['avg_nav']:.4f}")
        
        print(f"\n📈 Performance:")
        perf = result['performance']
        print(f"  Total Return: {perf['total_return']:.2f}%")
        print(f"  Avg Daily Return: {perf['avg_daily_return']:.4f}%")
        print(f"  Best Day: {perf['best_day']:.2f}%")
        print(f"  Worst Day: {perf['worst_day']:.2f}%")
        
        print(f"\n⚠️  Risk Profile:")
        risk = result['risk']
        print(f"  Volatility (30d): {risk['volatility_30d']:.2f}%")
        print(f"  Sharpe Ratio: {risk['sharpe_ratio']:.2f}")
        print(f"  Sortino Ratio: {risk['sortino_ratio']:.2f}")
        print(f"  Max Drawdown (1y): {risk['max_drawdown']:.2f}%")
        print(f"  Risk Level: {risk['risk_level']}")
        
        print(f"\n📊 Trend Analysis:")
        trend = result['trend']
        print(f"  Trend Direction: {trend['trend_direction']}")
        print(f"  Trend Strength (R²): {trend['trend_strength']:.4f}")
        print(f"  RSI: {trend['rsi']:.2f} ({trend['rsi_signal']})")
        print(f"  Golden Cross: {'✓ Yes' if trend['golden_cross'] else '✗ No'}")
        print(f"  Price > EMA: {'✓ Yes' if trend['price_above_ema'] else '✗ No'}")

# ===== Test 6: Get NAV Data =====
if first_scheme_code:
    print("\n" + "="*70)
    print("6️⃣  GET NAV DATA (Latest 5 records)")
    print("="*70)
    
    response = client.get(f"/api/schemes/{first_scheme_code}/nav?limit=5")
    print(f"\nGET /api/schemes/{first_scheme_code}/nav?limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total Records: {result['total_records']}")
        print(f"\nLatest 5 Records:")
        print(f"{'Date':<12} {'NAV':>12} {'Daily Return':>15} {'Cum Return':>15}")
        print("-" * 54)
        for rec in result['data']:
            daily = f"{rec['daily_return']:.2f}%" if rec['daily_return'] is not None else "N/A"
            cum = f"{rec['cumulative_return']:.2f}%" if rec['cumulative_return'] is not None else "N/A"
            print(f"{rec['date']:<12} ₹{rec['nav']:>11.4f} {daily:>14} {cum:>14}")

# ===== Test 7: Get Top Schemes =====
print("\n" + "="*70)
print("7️⃣  TOP SCHEMES BY SHARPE RATIO")
print("="*70)

response = client.get("/api/top-schemes?metric=sharpe_ratio&limit=5")
print(f"\nGET /api/top-schemes?metric=sharpe_ratio&limit=5")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nTop {len(result['results'])} Schemes by Sharpe Ratio:")
    print(f"{'Rank':<6} {'Sharpe Ratio':>14} {'Scheme Name':<30} {'Fund House':<20}")
    print("-" * 70)
    for rank in result['results']:
        scheme_name = rank['scheme_name'][:28]
        fund_house = rank['fund_house'][:18]
        print(f"{rank['rank']:<6} {rank['value']:>14.2f} {scheme_name:<30} {fund_house:<20}")

# ===== Test 8: Market Statistics =====
print("\n" + "="*70)
print("8️⃣  MARKET STATISTICS")
print("="*70)

response = client.get("/api/statistics")
print(f"\nGET /api/statistics")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nMarket Overview:")
    print(f"  Total Schemes: {result['total_schemes']:,}")
    print(f"  Total Records: {result['total_records']:,}")
    print(f"  Fund Houses: {result['total_fund_houses']}")
    print(f"  Date Range: {result['date_range']['start']} to {result['date_range']['end']}")
    
    print(f"\nNAV Statistics:")
    nav = result['nav_statistics']
    print(f"  Min: ₹{nav['min']:.4f}")
    print(f"  Max: ₹{nav['max']:.4f}")
    print(f"  Mean: ₹{nav['mean']:.4f}")
    print(f"  Median: ₹{nav['median']:.4f}")
    
    print(f"\nPerformance Statistics:")
    perf = result['performance_statistics']
    print(f"  Avg Volatility: {perf['avg_volatility']:.2f}%")
    print(f"  Avg Sharpe Ratio: {perf['avg_sharpe_ratio']:.2f}")

# ===== Test 9: Compare Schemes =====
if len(client.get("/api/schemes?limit=100").json()['schemes']) >= 3:
    print("\n" + "="*70)
    print("9️⃣  COMPARE SCHEMES")
    print("="*70)
    
    all_schemes = client.get("/api/schemes?limit=100").json()['schemes']
    codes = f"{all_schemes[0]['scheme_code']},{all_schemes[1]['scheme_code']},{all_schemes[2]['scheme_code']}"
    
    response = client.get(f"/api/compare?scheme_codes={codes}&sort_by=sharpe_ratio")
    print(f"\nGET /api/compare?scheme_codes={codes}&sort_by=sharpe_ratio")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nComparison Results (sorted by {result['sorted_by']}):")
        print(f"{'Scheme Name':<35} {'NAV':>12} {'Return':>12} {'Volatility':>12} {'Sharpe':>10}")
        print("-" * 80)
        for scheme in result['schemes']:
            name = scheme['scheme_name'][:33]
            print(f"{name:<35} ₹{scheme['current_nav']:>11.4f} {scheme['total_return']:>11.2f}% {scheme['volatility']:>11.2f}% {scheme['sharpe_ratio']:>9.2f}")

# ===== Test 10: Get Top Performing =====
print("\n" + "="*70)
print("🔟 TOP SCHEMES BY RETURN")
print("="*70)

response = client.get("/api/top-schemes?metric=return&limit=5")
print(f"\nGET /api/top-schemes?metric=return&limit=5")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nTop {len(result['results'])} Schemes by Return:")
    print(f"{'Rank':<6} {'Return %':>12} {'Scheme Name':<30} {'Fund House':<20}")
    print("-" * 70)
    for rank in result['results']:
        scheme_name = rank['scheme_name'][:28]
        fund_house = rank['fund_house'][:18]
        print(f"{rank['rank']:<6} {rank['value']:>11.2f}% {scheme_name:<30} {fund_house:<20}")

print("\n" + "="*70)
print("✓ API TESTING COMPLETE")
print("="*70)
print("\n📝 To run the API server, execute:")
print("   python -m uvicorn src.api.main:app --reload")
print("\n📚 API Documentation will be available at:")
print("   http://localhost:8000/docs  (Swagger UI)")
print("   http://localhost:8000/redoc (ReDoc)")
print("="*70)
