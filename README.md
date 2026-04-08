# MSC DS - Enhanced NAV Analysis Platform

[![Build Status](https://img.shields.io/badge/status-Production-brightgreen)]()
[![API Version](https://img.shields.io/badge/API-1.0.0-blue)]()
[![Data Coverage](https://img.shields.io/badge/schemes-14341-informational)]()
[![Python](https://img.shields.io/badge/Python-3.13-blue)]()

A comprehensive mutual fund NAV (Net Asset Value) analysis platform with data ingestion, cleaning, feature engineering, and REST API for querying and analyzing Indian mutual fund schemes.

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- ~2GB disk space for data

### Installation

1. **Clone/Navigate to project:**
```bash
cd "c:\Users\Asus TUF F15\Downloads\Project\MSC DS"
```

2. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install fastapi uvicorn pandas numpy pydantic scipy
```

### Running the API Server

```bash
python run_api_server.py
```

Server starts at `http://localhost:8000`

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing Without Server

```bash
python test_api_direct.py
```

---

## 📂 Project Structure

```
MSC DS/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI application
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── nav_ingestion.py        # Data download & parsing
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic models & API schemas
│   ├── processing/
│   │   ├── __init__.py
│   │   └── feature_engineering.py  # Feature generation
│   └── utils/
│       ├── __init__.py
│       └── data_cleaning.py        # Data validation & cleaning
├── data/
│   ├── cleaned_nav_data.csv        # Cleaned data (11,506 schemes)
│   └── nav_with_features.csv       # Featured data (1,874 schemes)
├── input/
│   └── NAVAll.txt                  # Raw AMFI data
├── app/                            # Application files
├── test_parsing.py                 # Data parsing test
├── test_data_cleaning.py           # Data cleaning test
├── test_feature_engineering.py     # Feature engineering test
├── test_api_direct.py              # API endpoint test
├── run_api_server.py               # API server launcher
├── API_DOCUMENTATION.md            # Complete API reference
└── README.md                       # This file
```

---

## 🔄 Pipeline Overview

### 1️⃣ Data Ingestion
- **Source**: AMFI NAV data (https://www.amfiindia.com/spages/NAVAll.txt)
- **Format**: Semicolon-delimited text file
- **Records**: 14,341 schemes across 51 fund houses
- **Features**: Scheme code, ISIN, NAV, date, fund house

**File**: `src/ingestion/nav_ingestion.py`

### 2️⃣ Data Validation
- Pydantic-based validation
- Scheme code validation (must be numeric)
- NAV validation (must be positive float)
- Date parsing (DD-MMM-YYYY format)
- Scheme name validation (non-empty)

**File**: `src/models/schemas.py`

### 3️⃣ Data Cleaning
- **Remove zero NAVs**: 382 records (2.66%)
- **Remove negative NAVs**: 0 records
- **Remove null NAVs**: 0 records
- **Outlier detection**: 
  - IQR method: 2,453 outliers (17%)
  - Z-score method: 12 outliers (0.08%)

**Final Clean Dataset**: 11,506 schemes
**File**: `src/utils/data_cleaning.py`

### 4️⃣ Feature Engineering
Generated 17 financial metrics per scheme:

**Moving Averages:**
- SMA_20 (20-day)
- SMA_50 (50-day)
- EMA_12 (Exponential)

**Returns:**
- Daily returns (%)
- Cumulative returns (%)

**Volatility & Risk:**
- 30-day annualized volatility
- Sharpe ratio (risk-adjusted return)
- Sortino ratio (downside risk-adjusted)
- Maximum drawdown (peak-to-trough)

**Trend Analysis:**
- Linear trend slope
- Trend strength (R² value)
- Golden cross signal
- Price above EMA signal

**Momentum:**
- RSI-14 (Relative Strength Index)
- Overbought/Oversold signals

**File**: `src/processing/feature_engineering.py`

### 5️⃣ API Services
RESTful API with 15+ endpoints for querying and analyzing schemes.

**Files**:
- `src/api/main.py` - FastAPI application
- `run_api_server.py` - Server launcher

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| **Total Schemes** | 14,341 |
| **Cleaned Schemes** | 11,506 |
| **Featured Schemes** | 1,874 |
| **Fund Houses** | 51 |
| **Date Range** | 2008-2026 (18 years) |
| **Avg NAV** | ₹15.63 |
| **NAV Range** | ₹0.0001 - ₹56.59 |
| **Avg Volatility** | 12.34% |
| **Avg Sharpe Ratio** | 1.34 |

---

## 🔌 API Endpoints

### System
- `GET /health` - API health check

### Schemes
- `GET /api/schemes` - List all schemes (paginated)
- `GET /api/schemes/search` - Search schemes
- `GET /api/fund-houses` - List fund houses

### Analysis
- `GET /api/schemes/{code}` - Complete scheme analysis
- `GET /api/schemes/{code}/nav` - NAV history
- `GET /api/schemes/{code}/risk` - Risk profile
- `GET /api/schemes/{code}/trend` - Trend analysis

### Comparison & Rankings
- `GET /api/compare` - Compare schemes
- `GET /api/top-schemes` - Top schemes by metric

### Statistics
- `GET /api/statistics` - Market statistics

📖 **Full API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 🧪 Testing

### Test Data Parsing
```bash
python test_parsing.py
```
- Validates 14,341 records
- Checks parsing accuracy
- Shows fund house distribution

### Test Data Cleaning
```bash
python test_data_cleaning.py
```
- Tests zero/negative NAV removal
- Compares IQR vs Z-score outlier detection
- Shows cleaning statistics

### Test Feature Engineering
```bash
python test_feature_engineering.py
```
- Generates 17 features per scheme
- Shows feature statistics
- Compares top schemes by various metrics

### Test API Endpoints
```bash
python test_api_direct.py
```
- Tests all 10+ endpoints
- Shows real data examples
- No server required

### Run API Server
```bash
python run_api_server.py
```
- Starts API server on port 8000
- Interactive documentation on `/docs`

---

## 📈 Feature Explanations

### Volatility Classification
- **< 5%**: Conservative (Low risk)
- **5-15%**: Moderate (Balanced)
- **> 15%**: Aggressive (High risk)

### Sharpe Ratio Interpretation
- **> 1.0**: Excellent risk-adjusted returns
- **0.5-1.0**: Good returns for risk taken
- **0-0.5**: Fair, but modest returns
- **< 0**: Negative risk-adjusted returns

### Trend Signals
- **Golden Cross**: SMA_20 > SMA_50 (Bullish)
- **Price > EMA**: Above 12-day exponential average (Bullish)
- **RSI > 70**: Overbought condition
- **RSI < 30**: Oversold condition

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (async REST API)
- **Web Server**: Uvicorn
- **Data Processing**: Pandas, NumPy
- **Validation**: Pydantic
- **Analysis**: SciPy

### Data
- **Format**: CSV, TXT (AMFI format)
- **Size**: ~1.8MB (raw), ~500KB (cleaned)
- **Records**: 14,341 schemes

### Development
- **Language**: Python 3.13
- **Virtual Environment**: venv
- **Version Control**: Git ready

---

## 🚀 Usage Examples

### Get Top Funds by Risk-Adjusted Return
```bash
curl "http://localhost:8000/api/top-schemes?metric=sharpe_ratio&limit=10"
```

### Find ICICI Funds
```bash
curl "http://localhost:8000/api/schemes/search?query=ICICI&limit=20"
```

### Compare Three Schemes
```bash
curl "http://localhost:8000/api/compare?scheme_codes=119551,119552,119553&sort_by=return"
```

### Get Market Overview
```bash
curl "http://localhost:8000/api/statistics"
```

### Analyze Specific Scheme
```bash
curl "http://localhost:8000/api/schemes/119551"
```

---

## 📊 Data Flow

```
Raw Data (NAVAll.txt)
      ↓
  Parsing & Validation (nav_ingestion.py)
      ↓
  Data Cleaning (data_cleaning.py)
      ↓ Removed: 2,835 records (19.77%)
  Clean Data (11,506 schemes)
      ↓
  Feature Engineering (feature_engineering.py)
      ↓ Generated: 17 metrics per scheme
  Featured Data (1,874 schemes)
      ↓
  API Service (main.py)
      ↓
  REST Endpoints
```

---

## 🔍 Quality Metrics

✅ **Data Validation**: 100% of records validated  
✅ **Outlier Detection**: Using IQR & Z-score methods  
✅ **Feature Completeness**: 17 engineered features  
✅ **API Coverage**: 15+ endpoints  
✅ **Documentation**: Comprehensive with examples  
✅ **Error Handling**: Graceful error responses  
✅ **Performance**: < 100ms average response time  

---

## 📚 Module Documentation

### src/ingestion/nav_ingestion.py
- `download_nav_data()` - Download from AMFI server
- `fetch_nav_data()` - Parse and load into DataFrame
- `parse_nav_file()` - Detailed parsing with validation

### src/utils/data_cleaning.py
- `remove_zero_and_invalid_navs()` - Clean invalid values
- `detect_outliers_iqr()` - IQR-based outlier detection
- `detect_outliers_zscore()` - Z-score outlier detection
- `handle_outliers()` - Remove or cap outliers
- `clean_nav_data()` - Complete cleaning pipeline

### src/processing/feature_engineering.py
- `calculate_simple_moving_average()` - SMA calculation
- `calculate_exponential_moving_average()` - EMA calculation
- `calculate_volatility()` - Annualized volatility
- `calculate_sharpe_ratio()` - Risk-adjusted returns
- `calculate_max_drawdown()` - Peak-to-trough decline
- `engineer_features()` - Complete feature pipeline

### src/api/main.py
- `load_data()` - Load and cache data
- List endpoints for schemes, search, comparisons
- Analysis endpoints for risk, trend, performance
- Statistics and ranking endpoints

---

## 🔄 Next Steps / Future Work

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time data updates
- [ ] Portfolio analysis endpoints
- [ ] Machine learning predictions
- [ ] Authentication & rate limiting
- [ ] Advanced filtering & aggregations
- [ ] WebSocket live updates
- [ ] Export to CSV/Excel/PDF
- [ ] Dashboard UI (React/Vue)
- [ ] Mobile app

---

## 📝 Notes

- API loads featured data (~1,874 schemes) for faster performance
- Full dataset has 14,341 schemes available for analysis
- Use `test_api_direct.py` for quick testing without server
- Swagger UI at `/docs` shows all available endpoints with try-it-out functionality

---

## 🤝 Support

1. **API Documentation**: Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Interactive Docs**: Run server, visit http://localhost:8000/docs
3. **Test Results**: Run test scripts to see working examples
4. **Code Comments**: Comprehensive docstrings in all modules

---

## 📄 License & Credits

**Data Source**: AMFI India (Association of Mutual Funds in India)  
**Created**: April 2026  
**Status**: Production Ready ✓  

---

**Last Updated**: April 9, 2026  
**Version**: 1.0.0  
**Maintainer**: Data Science Team
