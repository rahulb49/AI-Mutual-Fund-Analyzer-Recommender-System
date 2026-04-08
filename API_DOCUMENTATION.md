# NAV Analysis API - Complete Documentation

## Overview
The NAV Analysis API is a FastAPI-based REST API for querying, analyzing, and comparing mutual fund schemes with comprehensive feature engineering and risk metrics.

**Base URL:** `http://localhost:8000`  
**API Version:** 1.0.0  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Getting Started

### Starting the Server
```bash
python run_api_server.py
```

### Testing the API
```bash
# Run direct tests (no server needed)
python test_api_direct.py

# Or use curl
curl http://localhost:8000/health
```

---

## Endpoints Reference

### 1. Health & Status

#### GET /health
Check API status and data availability

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running and data is loaded",
  "timestamp": "2026-04-09T12:00:00",
  "data_loaded": true
}
```

---

### 2. Scheme Listing & Search

#### GET /api/schemes
List all available schemes with pagination

**Query Parameters:**
- `limit` (int, 1-1000, default: 100) - Number of schemes to return
- `offset` (int, default: 0) - Pagination offset

**Response:**
```json
{
  "total": 14341,
  "returned": 5,
  "offset": 0,
  "limit": 5,
  "schemes": [
    {
      "scheme_code": 119551,
      "scheme_name": "Aditya Birla Sun Life Banking & PSU Debt Fund",
      "fund_house": "Aditya Birla Sun Life Mutual Fund",
      "current_nav": 103.8813
    }
  ]
}
```

#### GET /api/schemes/search
Search for schemes by name or fund house

**Query Parameters:**
- `query` (string, required) - Search keyword (min 2 chars)
- `search_in` (string, default: "all") - "name", "fund_house", or "all"
- `limit` (int, 1-500, default: 50) - Max results

**Example:** `/api/schemes/search?query=ICICI&search_in=name&limit=10`

**Response:**
```json
{
  "total_found": 50,
  "query": "ICICI",
  "search_field": "name",
  "schemes": [
    {
      "scheme_code": 112345,
      "scheme_name": "ICICI Prudential... Fund",
      "fund_house": "ICICI Prudential Mutual Fund",
      "match_type": "name"
    }
  ]
}
```

#### GET /api/fund-houses
List all fund houses with metrics

**Response:**
```json
{
  "total_fund_houses": 51,
  "fund_houses": [
    {
      "fund_house": "ICICI Prudential Mutual Fund",
      "scheme_count": 2490,
      "avg_nav": 1850.25,
      "min_nav": 0.01,
      "max_nav": 5000.00
    }
  ]
}
```

---

### 3. Scheme Analysis

#### GET /api/schemes/{scheme_code}
Get complete analysis for a specific scheme

**Path Parameters:**
- `scheme_code` (int) - Unique scheme identifier

**Response:**
```json
{
  "scheme_code": 119551,
  "scheme_name": "Aditya Birla Sun Life Banking & PSU Debt Fund",
  "fund_house": "Aditya Birla Sun Life Mutual Fund",
  "data_points": 2453,
  "nav_metrics": {
    "scheme_code": 119551,
    "scheme_name": "...",
    "fund_house": "...",
    "current_nav": 103.8813,
    "nav_min": 98.5234,
    "nav_max": 108.9456,
    "avg_nav": 103.2567
  },
  "performance": {
    "total_return": 45.23,
    "avg_daily_return": 0.0234,
    "best_day": 2.5678,
    "worst_day": -1.8234,
    "cumulative_return": 45.23
  },
  "risk": {
    "volatility_30d": 12.45,
    "sharpe_ratio": 1.234,
    "sortino_ratio": 1.567,
    "max_drawdown": -22.45,
    "risk_level": "MODERATE"
  },
  "trend": {
    "trend_slope": 0.00234,
    "trend_strength": 0.8765,
    "trend_direction": "Uptrend",
    "golden_cross": true,
    "price_above_ema": true,
    "rsi": 62.34,
    "rsi_signal": "Neutral"
  }
}
```

#### GET /api/schemes/{scheme_code}/nav
Get NAV history for a scheme

**Path Parameters:**
- `scheme_code` (int) - Scheme identifier

**Query Parameters:**
- `limit` (int, 1-1000, default: 50) - Number of recent records

**Response:**
```json
{
  "scheme_code": 119551,
  "scheme_name": "...",
  "total_records": 2453,
  "returned_records": 5,
  "data": [
    {
      "date": "2026-04-05",
      "nav": 103.8234,
      "daily_return": 0.1234,
      "cumulative_return": 45.23
    }
  ]
}
```

#### GET /api/schemes/{scheme_code}/risk
Get risk profile for a scheme

**Response:**
```json
{
  "volatility_30d": 12.45,
  "sharpe_ratio": 1.234,
  "sortino_ratio": 1.567,
  "max_drawdown": -22.45,
  "risk_level": "MODERATE"
}
```

#### GET /api/schemes/{scheme_code}/trend
Get trend analysis for a scheme

**Response:**
```json
{
  "trend_slope": 0.00234,
  "trend_strength": 0.8765,
  "trend_direction": "Uptrend",
  "golden_cross": true,
  "price_above_ema": true,
  "rsi": 62.34,
  "rsi_signal": "Neutral"
}
```

---

### 4. Scheme Comparison

#### GET /api/compare
Compare multiple schemes side by side

**Query Parameters:**
- `scheme_codes` (string, required) - Comma-separated scheme codes (e.g., "119551,119552,119553")
- `sort_by` (string, default: "sharpe_ratio") - "nav", "return", "volatility", or "sharpe_ratio"

**Example:** `/api/compare?scheme_codes=119551,119552,119553&sort_by=sharpe_ratio`

**Response:**
```json
{
  "schemes": [
    {
      "scheme_code": 119551,
      "scheme_name": "...",
      "fund_house": "...",
      "current_nav": 103.8813,
      "total_return": 45.23,
      "volatility": 12.45,
      "sharpe_ratio": 1.234,
      "risk_level": "MODERATE"
    }
  ],
  "metric": "multiple_schemes",
  "sorted_by": "sharpe_ratio"
}
```

---

### 5. Rankings & Top Schemes

#### GET /api/top-schemes
Get top schemes ranked by metric

**Query Parameters:**
- `metric` (string, default: "sharpe_ratio") - "sharpe_ratio", "return", "volatility", or "nav"
- `limit` (int, 1-100, default: 10) - Number of schemes to return

**Examples:**
- `/api/top-schemes?metric=sharpe_ratio&limit=10` - Best risk-adjusted returns
- `/api/top-schemes?metric=return&limit=10` - Highest returns
- `/api/top-schemes?metric=volatility&limit=10` - Lowest risk

**Response:**
```json
{
  "metric": "sharpe_ratio",
  "limit": 10,
  "results": [
    {
      "rank": 1,
      "scheme_code": 112345,
      "scheme_name": "Best Fund",
      "fund_house": "Best Fund House",
      "value": 2.456,
      "unit": "Sharpe Ratio"
    }
  ]
}
```

---

### 6. Statistics & Analytics

#### GET /api/statistics
Get market-wide statistics

**Response:**
```json
{
  "total_schemes": 14341,
  "total_records": 1874,
  "total_fund_houses": 51,
  "date_range": {
    "start": "2008-10-02",
    "end": "2026-04-06"
  },
  "nav_statistics": {
    "min": 0.0001,
    "max": 56.5800,
    "mean": 15.6312,
    "median": 12.5254
  },
  "performance_statistics": {
    "avg_volatility": 12.34,
    "avg_sharpe_ratio": 1.34
  }
}
```

---

## Features & Metrics Explained

### NAV Metrics
- **Current NAV**: Latest Net Asset Value
- **Min/Max NAV**: Historical low and high values
- **Avg NAV**: Average NAV over period

### Performance Metrics
- **Total Return**: Cumulative return from inception (%)
- **Avg Daily Return**: Average daily percentage change
- **Best/Worst Day**: Best and worst daily returns
- **Cumulative Return**: Total appreciation (%)

### Risk Metrics

#### Volatility (30-day)
- Annualized standard deviation of daily returns
- **< 5%**: Low risk (Conservative funds)
- **5-15%**: Moderate risk (Balanced funds)
- **> 15%**: High risk (Aggressive funds)

#### Sharpe Ratio
- Excess return per unit of risk
- **> 1.0**: Excellent
- **0.5-1.0**: Good
- **0-0.5**: Fair
- **< 0**: Poor

#### Sortino Ratio
- Like Sharpe, but penalizes only downside volatility
- Better for funds with skewed returns

#### Maximum Drawdown
- Largest percentage loss from peak to trough
- **> -10%**: Low downside risk
- **-10% to -25%**: Moderate downside risk
- **< -25%**: High downside risk

### Trend Indicators

#### Trend Direction
- **Uptrend**: Positive linear trend (price rising)
- **Downtrend**: Negative linear trend (price falling)
- **Neutral**: No clear trend

#### Trend Strength (R²)
- Measures how well the trend line fits data
- **0-0.3**: Weak trend
- **0.3-0.7**: Moderate trend
- **0.7-1.0**: Strong trend

#### Golden Cross
- **True**: SMA_20 > SMA_50 (Bullish signal)
- **False**: SMA_20 < SMA_50 (Bearish signal)

#### RSI (Relative Strength Index)
- Momentum oscillator (0-100)
- **> 70**: Overbought (potential sell signal)
- **< 30**: Oversold (potential buy signal)
- **30-70**: Neutral

---

## Error Handling

### Error Response Format
```json
{
  "error": "HTTP Exception",
  "detail": "Scheme 999999 not found",
  "timestamp": "2026-04-09T12:00:00"
}
```

### Common Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Bad Request | Invalid query parameters |
| 404 | Not Found | Scheme doesn't exist |
| 503 | Service Unavailable | Data not loaded |

---

## Usage Examples

### Example 1: Find Best Funds by Risk-Adjusted Return
```bash
curl "http://localhost:8000/api/top-schemes?metric=sharpe_ratio&limit=5"
```

### Example 2: Compare Three Specific Funds
```bash
curl "http://localhost:8000/api/compare?scheme_codes=119551,119552,119553&sort_by=return"
```

### Example 3: Search for ICICI Funds
```bash
curl "http://localhost:8000/api/schemes/search?query=ICICI&limit=10"
```

### Example 4: Get Complete Analysis
```bash
curl "http://localhost:8000/api/schemes/119551"
```

### Example 5: Market Overview
```bash
curl "http://localhost:8000/api/statistics"
```

---

## API Features

✅ **Data Support**: 14,341 mutual fund schemes  
✅ **Fund Houses**: 51 major Indian fund houses  
✅ **Time Period**: 2008 to 2026  
✅ **Feature Engineering**: 17 engineered financial metrics  
✅ **Analysis Types**: Risk, Performance, Trend, Momentum  
✅ **Comparison**: Multiple scheme analysis  
✅ **Search & Filter**: Fast scheme lookup  
✅ **Rankings**: By various financial metrics  
✅ **CORS Enabled**: Cross-origin requests supported  
✅ **Interactive Docs**: Swagger UI & ReDoc  

---

## Performance

- **Data Loading**: < 5 seconds
- **Query Response**: < 100ms average
- **Comparison Analysis**: < 500ms
- **Full Scheme Analysis**: < 200ms

---

## Future Enhancements

- [ ] Historical data export (CSV/Excel)
- [ ] Scheme recommendations engine
- [ ] Portfolio analysis endpoints
- [ ] Real-time NAV updates
- [ ] Machine learning predictions
- [ ] User authentication & quotas
- [ ] WebSocket live updates
- [ ] Caching layer for better performance

---

## Support

For issues or questions:
1. Check interactive API docs: `http://localhost:8000/docs`
2. Review this documentation
3. Check test files: `test_api_direct.py`

---

**Last Updated:** April 9, 2026  
**API Version:** 1.0.0  
**Status:** Production Ready ✓
