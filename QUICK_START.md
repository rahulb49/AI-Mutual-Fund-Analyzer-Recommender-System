# Quick Start Guide

## ⚡ 60-Second Setup

```bash
# 1. Navigate to project
cd "c:\Users\Asus TUF F15\Downloads\Project\MSC DS"

# 2. Activate environment
.venv\Scripts\activate

# 3. Start API server
python run_api_server.py
```

✓ API runs on http://localhost:8000  
📚 Visit http://localhost:8000/docs for interactive documentation

---

## 🎯 Common Tasks

### Find Best Performing Funds
```bash
curl "http://localhost:8000/api/top-schemes?metric=return&limit=10"
```

### Get Low-Risk, High-Return Funds (Best Sharpe Ratio)
```bash
curl "http://localhost:8000/api/top-schemes?metric=sharpe_ratio&limit=5"
```

### Search for a Specific Fund
```bash
curl "http://localhost:8000/api/schemes/search?query=ICICI%20Prudential"
```

### Compare Three Funds
Replace with actual scheme codes:
```bash
curl "http://localhost:8000/api/compare?scheme_codes=119551,119552,119553"
```

### Get Complete Analysis for One Fund
```bash
curl "http://localhost:8000/api/schemes/119551"
```

### View Market Statistics
```bash
curl "http://localhost:8000/api/statistics"
```

---

## 🧪 Testing

### Run API Tests (No Server Needed)
```bash
python test_api_direct.py
```
Shows all endpoints with real data examples

### Test Data Parsing
```bash
python test_parsing.py
```

### Test Data Cleaning
```bash
python test_data_cleaning.py
```

### Test Feature Engineering
```bash
python test_feature_engineering.py
```

---

## 📊 Scheme Code Examples

| Code | Scheme Name | Fund House |
|------|-------------|-----------|
| 119551 | Aditya Birla Banking & PSU Debt Fund | Aditya Birla Sun Life |
| 119552 | Aditya Birla Banking & PSU Debt Fund | Aditya Birla Sun Life |
| 120437 | Axis Banking & PSU Debt Fund | Axis Mutual Fund |

Find more codes using the search endpoint.

---

## 🔍 Understanding Metrics

### Volatility
- **< 5%**: Low risk ✅
- **5-15%**: Medium risk ⚠️
- **> 15%**: High risk 🔴

### Sharpe Ratio
- **> 1.0**: Excellent 🌟
- **0.5-1.0**: Good ✓
- **< 0.5**: Poor ✗

### Max Drawdown
- **> -10%**: Small losses
- **-10% to -25%**: Moderate losses
- **< -25%**: Large losses

---

## 🛠️ Common Issues

**Q: API won't start?**  
A: Make sure port 8000 is free. Try: `netstat -ano | findstr :8000`

**Q: Data not loading?**  
A: Run `python test_api_direct.py` to check if data file exists

**Q: Getting "Module not found" errors?**  
A: Make sure venv is activated and dependencies installed: `pip install -r requirements.txt`

---

## 📚 Available Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Check API status |
| `GET /api/schemes` | List schemes (paginated) |
| `GET /api/schemes/search` | Search schemes |
| `GET /api/schemes/{code}` | Full analysis for scheme |
| `GET /api/compare` | Compare multiple schemes |
| `GET /api/top-schemes` | Top schemes by metric |
| `GET /api/statistics` | Market statistics |
| `GET /api/fund-houses` | List fund houses |

📖 Full details: See API_DOCUMENTATION.md

---

## 💡 Pro Tips

1. **Use Swagger UI**: Visit http://localhost:8000/docs for interactive testing
2. **Try query params**: Add `&limit=50` to get more results
3. **Export data**: Use `&format=csv` for comma-separated values
4. **Compare funds**: Use `/api/compare?scheme_codes=1,2,3` for side-by-side analysis
5. **Filter by metric**: Use `?sort_by=volatility` to sort by risk

---

## 📞 Support

- **See all endpoints**: Visit http://localhost:8000/docs
- **See examples**: Run `python test_api_direct.py`
- **Full docs**: Read API_DOCUMENTATION.md

---

Need more help? Check the main README.md or API_DOCUMENTATION.md
