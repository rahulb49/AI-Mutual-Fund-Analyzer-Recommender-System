# Streamlit Dashboard Configuration
import os

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

# Data Files
FEATURED_DATA = os.path.join(DATA_DIR, "nav_with_features.csv")
CLEANED_DATA = os.path.join(DATA_DIR, "cleaned_nav_data.csv")

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Color Scheme
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff9800",
    "info": "#17a2b8",
}

# Chart Configuration
CHART_CONFIG = {
    "height": 400,
    "use_container_width": True,
}

# Risk Thresholds
RISK_LEVELS = {
    "low": (0, 5),
    "moderate": (5, 15),
    "high": (15, float("inf")),
}

# Sharpe Ratio Thresholds
SHARPE_LEVELS = {
    "excellent": (1.0, float("inf")),
    "good": (0.5, 1.0),
    "fair": (0.0, 0.5),
    "poor": (float("-inf"), 0.0),
}
