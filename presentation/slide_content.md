Title: AI Mutual Fund Analyzer & Recommender System
Subtitle: End-to-end project overview

---

Slide: Objectives
- Build an end-to-end pipeline to ingest NAV data, engineer features, rank and recommend mutual funds.
- Demonstrate Airflow orchestration, FastAPI backend, and Streamlit dashboard.

---

Slide: Tech Stack
- Python 3.10
- Airflow (Docker Compose)
- FastAPI + Uvicorn (API)
- Streamlit (Dashboard)
- Pandas, NumPy, scikit-learn, Plotly

---

Slide: Architecture Diagram
Notes: See diagrams/architecture.mmd for the architecture mermaid source.

---

Slide: Data Sources
- AMFI NAVAll.txt (live fallback)
- Local CSVs: data/cleaned_nav_data.csv, data/nav_with_features.csv

---

Slide: Ingestion & Feature Engineering
- Airflow DAGs ingest raw NAV, clean, and run feature engineering.
- Key features: volatility (30d), Sharpe, RSI, moving averages, drawdown.

---

Slide: API Layer
- FastAPI exposes endpoints for scheme search, recommendations, and rankings.
- Caches engineered features for performance.

---

Slide: Dashboard / UX
- Streamlit pages: Dashboard, Scheme Search, Comparison, Rankings, Statistics, ML clusters, ML rankings, ML recommendations.
- Compact info buttons added next to metrics for one-line explanations.

---

Slide: Deployment Notes
- Streamlit Cloud: UI-only requirements.txt (no backend pins).
- Airflow runs via Docker Compose locally or remote server.

---

Slide: Demo Steps
1. Start Airflow (Docker Compose)
2. Start API: `python run_api_server.py`
3. Start Dashboard: `python run_dashboard.py`
4. Show live fallback (AMFI download) when CSVs missing

---

Slide: Known Issues & Future Work
- Streamlit Cloud redeploy must pick latest commits to use live fallback.
- Future: persist engineered features, add auth, production CI/CD.

---

Slide: References
- Repository: local workspace
- AMFI NAV: https://www.amfiindia.com/spages/NAVAll.txt

---

Slide: Thank you
Contact: (Your Name) — Q&A
