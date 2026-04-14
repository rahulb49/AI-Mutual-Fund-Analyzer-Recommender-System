"""
FastAPI Application for NAV Data Analysis
Provides endpoints for querying, analyzing, and comparing mutual fund schemes
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import (
    NavMetricsResponse, PerformanceMetricsResponse, RiskMetricsResponse,
    TrendAnalysisResponse, SchemeAnalysisResponse, ComparisonResponse,
    ComparisonSchemeResponse, SearchResponse, HealthResponse, ErrorResponse
)
from processing.feature_engineering import (
    engineer_features, generate_feature_summary, FeatureConfig
)
from machine_learning import cluster_funds, rank_funds, recommend_funds
from machine_learning.config import ClusteringConfig, RankingWeights, RecommendationConfig

# ===== App Configuration =====
app = FastAPI(
    title="NAV Analysis API",
    description="Comprehensive Mutual Fund NAV Analysis and Feature Engineering API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Global State =====
class DataCache:
    """In-memory data cache"""
    def __init__(self):
        self.df = None
        self.df_features = None
        self.schemes_dict = {}
        self.loaded = False
        self.config = FeatureConfig()

cache = DataCache()


def load_data():
    """Load NAV data and engineer features (called at startup)"""
    try:
        data_file = Path(__file__).parent.parent.parent / "data" / "nav_with_features.csv"
        
        if not data_file.exists():
            print(f"⚠️  Featured data not found. Trying cleaned data...")
            data_file = Path(__file__).parent.parent.parent / "data" / "cleaned_nav_data.csv"
        
        if not data_file.exists():
            print(f"❌ Data file not found at {data_file}")
            cache.loaded = False
            return False
        
        cache.df = pd.read_csv(data_file)
        cache.df['date'] = pd.to_datetime(cache.df['date'])
        
        # Check if features are already computed
        if 'volatility_30d' not in cache.df.columns:
            print("📊 Engineering features...")
            cache.df_features = cache.df.copy()
            for i, (name, group) in enumerate(cache.df.groupby('scheme_code')):
                try:
                    featured = engineer_features(group.copy(), cache.config)
                    cache.df_features.loc[featured.index] = featured
                except Exception as e:
                    print(f"  ⚠️  Error for scheme {name}: {str(e)[:50]}")
                
                if (i + 1) % 100 == 0:
                    print(f"  Processed {i + 1} schemes...")
        else:
            cache.df_features = cache.df.copy()
        
        # Build schemes dictionary for fast lookup
        cache.schemes_dict = cache.df.groupby('scheme_code').apply(
            lambda x: {
                'scheme_name': x['scheme_name'].iloc[0],
                'fund_house': x['fund_house'].iloc[0] if 'fund_house' in x.columns else 'Unknown'
            }
        ).to_dict()
        
        cache.loaded = True
        print(f"✓ Data loaded successfully: {len(cache.df):,} records")
        return True
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        cache.loaded = False
        return False


# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    """Load data on application startup"""
    load_data()


# ===== Health Check Endpoint =====
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health and data availability"""
    return HealthResponse(
        status="healthy" if cache.loaded else "degraded",
        message="API is running and data is loaded" if cache.loaded else "API is running but data is not loaded",
        timestamp=datetime.now(),
        data_loaded=cache.loaded
    )


# ===== Helper Functions =====
def get_scheme_data(scheme_code: int) -> Optional[pd.DataFrame]:
    """Get all data for a specific scheme"""
    if not cache.loaded or cache.df is None:
        return None
    
    scheme_data = cache.df_features[cache.df_features['scheme_code'] == scheme_code]
    return scheme_data if len(scheme_data) > 0 else None


def extract_nav_metrics(data: pd.DataFrame) -> NavMetricsResponse:
    """Extract NAV metrics from scheme data"""
    return NavMetricsResponse(
        scheme_code=int(data['scheme_code'].iloc[0]),
        scheme_name=data['scheme_name'].iloc[0],
        fund_house=data['fund_house'].iloc[0] if 'fund_house' in data.columns else 'Unknown',
        current_nav=float(data['net_asset_value'].iloc[-1]),
        nav_min=float(data['net_asset_value'].min()),
        nav_max=float(data['net_asset_value'].max()),
        avg_nav=float(data['net_asset_value'].mean())
    )


def extract_performance_metrics(data: pd.DataFrame) -> PerformanceMetricsResponse:
    """Extract performance metrics"""
    if 'daily_return' not in data.columns:
        return PerformanceMetricsResponse(
            total_return=0.0, avg_daily_return=0.0, best_day=0.0, worst_day=0.0, cumulative_return=0.0
        )
    
    return PerformanceMetricsResponse(
        total_return=float(data['cum_return'].iloc[-1]) if 'cum_return' in data.columns else 0.0,
        avg_daily_return=float(data['daily_return'].mean()),
        best_day=float(data['daily_return'].max()),
        worst_day=float(data['daily_return'].min()),
        cumulative_return=float(data['cum_return'].iloc[-1]) if 'cum_return' in data.columns else 0.0
    )


def extract_risk_metrics(data: pd.DataFrame) -> RiskMetricsResponse:
    """Extract risk metrics"""
    volatility = 0.0
    sharpe = 0.0
    sortino = 0.0
    drawdown = 0.0
    
    if 'volatility_30d' in data.columns and not data['volatility_30d'].iloc[-1:].isna().any():
        volatility = float(data['volatility_30d'].iloc[-1])
    if 'sharpe_ratio_30d' in data.columns and not data['sharpe_ratio_30d'].iloc[-1:].isna().any():
        sharpe = float(data['sharpe_ratio_30d'].iloc[-1])
    if 'sortino_ratio_30d' in data.columns and not data['sortino_ratio_30d'].iloc[-1:].isna().any():
        sortino = float(data['sortino_ratio_30d'].iloc[-1])
    if 'max_drawdown_1y' in data.columns and not data['max_drawdown_1y'].iloc[-1:].isna().any():
        drawdown = float(data['max_drawdown_1y'].iloc[-1])
    
    # Categorize risk level
    if volatility < 5:
        risk_level = "LOW"
    elif volatility < 15:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"
    
    return RiskMetricsResponse(
        volatility_30d=volatility,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        max_drawdown=drawdown,
        risk_level=risk_level
    )


def extract_trend_metrics(data: pd.DataFrame) -> TrendAnalysisResponse:
    """Extract trend metrics"""
    trend_slope = 0.0
    trend_strength = 0.0
    trend_dir = "Neutral"
    rsi = 50.0
    rsi_signal = "Neutral"
    
    if 'trend_slope' in data.columns and not data['trend_slope'].iloc[-1:].isna().any():
        trend_slope = float(data['trend_slope'].iloc[-1])
        if trend_slope > 0:
            trend_dir = "Uptrend"
        elif trend_slope < 0:
            trend_dir = "Downtrend"
    
    if 'trend_strength' in data.columns and not data['trend_strength'].iloc[-1:].isna().any():
        trend_strength = float(data['trend_strength'].iloc[-1])
    
    if 'rsi_14' in data.columns and not data['rsi_14'].iloc[-1:].isna().any():
        rsi = float(data['rsi_14'].iloc[-1])
        if rsi > 70:
            rsi_signal = "Overbought"
        elif rsi < 30:
            rsi_signal = "Oversold"
    
    golden_cross = bool(data['golden_cross'].iloc[-1]) if 'golden_cross' in data.columns else False
    price_above_ema = bool(data['price_above_ema'].iloc[-1]) if 'price_above_ema' in data.columns else False
    
    return TrendAnalysisResponse(
        trend_slope=trend_slope,
        trend_strength=trend_strength,
        trend_direction=trend_dir,
        golden_cross=golden_cross,
        price_above_ema=price_above_ema,
        rsi=rsi,
        rsi_signal=rsi_signal
    )


# ===== NAV Query Endpoints =====
@app.get("/api/schemes", response_model=dict, tags=["Schemes"])
async def list_all_schemes(
    limit: int = Query(100, ge=1, le=1000, description="Number of schemes to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List all available mutual fund schemes with pagination"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    schemes = []
    unique_schemes = cache.df.drop_duplicates('scheme_code')
    
    for _, row in unique_schemes.iloc[offset:offset+limit].iterrows():
        schemes.append({
            'scheme_code': int(row['scheme_code']),
            'scheme_name': row['scheme_name'],
            'fund_house': row['fund_house'] if 'fund_house' in row else 'Unknown',
            'current_nav': float(row['net_asset_value'])
        })
    
    return {
        'total': len(unique_schemes),
        'returned': len(schemes),
        'offset': offset,
        'limit': limit,
        'schemes': schemes
    }


@app.get("/api/schemes/search", response_model=SearchResponse, tags=["Schemes"])
async def search_schemes(
    query: str = Query(..., min_length=2, description="Search query"),
    search_in: str = Query("all", description="Search in: name, fund_house, or all"),
    limit: int = Query(50, ge=1, le=500)
):
    """Search for schemes by name or fund house"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    df_search = cache.df.drop_duplicates('scheme_code')
    results = []
    
    query_lower = query.lower()
    
    if search_in in ["name", "all"]:
        name_matches = df_search[df_search['scheme_name'].str.lower().str.contains(query_lower, na=False)]
        for _, row in name_matches.head(limit).iterrows():
            results.append({
                'scheme_code': int(row['scheme_code']),
                'scheme_name': row['scheme_name'],
                'fund_house': row['fund_house'] if 'fund_house' in row else 'Unknown',
                'match_type': 'name'
            })
    
    if search_in in ["fund_house", "all"]:
        fund_matches = df_search[df_search['fund_house'].str.lower().str.contains(query_lower, na=False)]
        for _, row in fund_matches.head(limit).iterrows():
            if not any(r['scheme_code'] == int(row['scheme_code']) for r in results):
                results.append({
                    'scheme_code': int(row['scheme_code']),
                    'scheme_name': row['scheme_name'],
                    'fund_house': row['fund_house'] if 'fund_house' in row else 'Unknown',
                    'match_type': 'fund_house'
                })
    
    return SearchResponse(
        total_found=len(results),
        schemes=results[:limit],
        query=query,
        search_field=search_in
    )


# ===== Scheme Analysis Endpoints =====
@app.get("/api/schemes/{scheme_code}", response_model=SchemeAnalysisResponse, tags=["Analysis"])
async def get_scheme_analysis(scheme_code: int):
    """Get complete analysis for a specific scheme"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    scheme_data = get_scheme_data(scheme_code)
    if scheme_data is None or len(scheme_data) == 0:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_code} not found")
    
    return SchemeAnalysisResponse(
        scheme_code=scheme_code,
        scheme_name=scheme_data['scheme_name'].iloc[0],
        fund_house=scheme_data['fund_house'].iloc[0] if 'fund_house' in scheme_data.columns else 'Unknown',
        nav_metrics=extract_nav_metrics(scheme_data),
        performance=extract_performance_metrics(scheme_data),
        risk=extract_risk_metrics(scheme_data),
        trend=extract_trend_metrics(scheme_data),
        data_points=len(scheme_data)
    )


@app.get("/api/schemes/{scheme_code}/nav", tags=["Data"])
async def get_scheme_nav_data(
    scheme_code: int,
    limit: int = Query(50, ge=1, le=1000, description="Number of recent records")
):
    """Get NAV data for a scheme (latest N records)"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    scheme_data = get_scheme_data(scheme_code)
    if scheme_data is None or len(scheme_data) == 0:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_code} not found")
    
    recent = scheme_data.sort_values('date').tail(limit)
    records = []
    
    for _, row in recent.iterrows():
        records.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'nav': float(row['net_asset_value']),
            'daily_return': float(row['daily_return']) if 'daily_return' in row else None,
            'cumulative_return': float(row['cum_return']) if 'cum_return' in row else None
        })
    
    return {
        'scheme_code': scheme_code,
        'scheme_name': scheme_data['scheme_name'].iloc[0],
        'total_records': len(scheme_data),
        'returned_records': len(records),
        'data': records
    }


@app.get("/api/schemes/{scheme_code}/risk", response_model=RiskMetricsResponse, tags=["Analysis"])
async def get_scheme_risk_profile(scheme_code: int):
    """Get detailed risk profile for a scheme"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    scheme_data = get_scheme_data(scheme_code)
    if scheme_data is None or len(scheme_data) == 0:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_code} not found")
    
    return extract_risk_metrics(scheme_data)


@app.get("/api/schemes/{scheme_code}/trend", response_model=TrendAnalysisResponse, tags=["Analysis"])
async def get_scheme_trend_analysis(scheme_code: int):
    """Get trend analysis for a scheme"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    scheme_data = get_scheme_data(scheme_code)
    if scheme_data is None or len(scheme_data) == 0:
        raise HTTPException(status_code=404, detail=f"Scheme {scheme_code} not found")
    
    return extract_trend_metrics(scheme_data)


# ===== Comparison Endpoints =====
@app.get("/api/compare", response_model=ComparisonResponse, tags=["Comparison"])
async def compare_schemes(
    scheme_codes: str = Query(..., description="Comma-separated scheme codes"),
    sort_by: str = Query("sharpe_ratio", description="Sort by: nav, return, volatility, sharpe_ratio")
):
    """Compare multiple schemes side by side"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        codes = [int(x.strip()) for x in scheme_codes.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheme codes format")
    
    comparison_schemes = []
    
    for code in codes:
        scheme_data = get_scheme_data(code)
        if scheme_data is not None and len(scheme_data) > 0:
            nav_metrics = extract_nav_metrics(scheme_data)
            risk_metrics = extract_risk_metrics(scheme_data)
            perf = extract_performance_metrics(scheme_data)
            
            comparison_schemes.append(ComparisonSchemeResponse(
                scheme_code=code,
                scheme_name=nav_metrics.scheme_name,
                fund_house=nav_metrics.fund_house,
                current_nav=nav_metrics.current_nav,
                total_return=perf.total_return,
                volatility=risk_metrics.volatility_30d,
                sharpe_ratio=risk_metrics.sharpe_ratio,
                risk_level=risk_metrics.risk_level
            ))
    
    # Sort based on parameter
    if sort_by == "nav":
        comparison_schemes.sort(key=lambda x: x.current_nav, reverse=True)
    elif sort_by == "return":
        comparison_schemes.sort(key=lambda x: x.total_return, reverse=True)
    elif sort_by == "volatility":
        comparison_schemes.sort(key=lambda x: x.volatility)
    elif sort_by == "sharpe_ratio":
        comparison_schemes.sort(key=lambda x: x.sharpe_ratio, reverse=True)
    
    return ComparisonResponse(
        schemes=comparison_schemes,
        metric="multiple_schemes",
        sorted_by=sort_by
    )


@app.get("/api/fund-houses", tags=["Fund Houses"])
async def list_fund_houses():
    """List all fund houses with scheme counts"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    fund_houses = cache.df.groupby('fund_house').agg({
        'scheme_code': 'nunique',
        'net_asset_value': ['min', 'max', 'mean']
    }).round(2)
    
    results = []
    for fund_house, row in fund_houses.iterrows():
        results.append({
            'fund_house': fund_house,
            'scheme_count': int(row[('scheme_code', 'nunique')]),
            'avg_nav': float(row[('net_asset_value', 'mean')]),
            'min_nav': float(row[('net_asset_value', 'min')]),
            'max_nav': float(row[('net_asset_value', 'max')])
        })
    
    results.sort(key=lambda x: x['scheme_count'], reverse=True)
    
    return {
        'total_fund_houses': len(results),
        'fund_houses': results
    }


# ===== Statistics Endpoints =====
@app.get("/api/statistics", tags=["Statistics"])
async def get_market_statistics():
    """Get overall market statistics"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    df = cache.df
    
    if 'volatility_30d' in df.columns and 'sharpe_ratio_30d' in df.columns:
        avg_volatility = float(df['volatility_30d'].mean())
        avg_sharpe = float(df['sharpe_ratio_30d'].mean())
    else:
        avg_volatility = 0.0
        avg_sharpe = 0.0
    
    return {
        'total_schemes': len(df.drop_duplicates('scheme_code')),
        'total_records': len(df),
        'total_fund_houses': df['fund_house'].nunique(),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d'),
            'end': df['date'].max().strftime('%Y-%m-%d')
        },
        'nav_statistics': {
            'min': float(df['net_asset_value'].min()),
            'max': float(df['net_asset_value'].max()),
            'mean': float(df['net_asset_value'].mean()),
            'median': float(df['net_asset_value'].median())
        },
        'performance_statistics': {
            'avg_volatility': avg_volatility,
            'avg_sharpe_ratio': avg_sharpe
        }
    }


# ===== Top Schemes Endpoints =====
@app.get("/api/top-schemes", tags=["Rankings"])
async def get_top_schemes(
    metric: str = Query("sharpe_ratio", description="Metric: sharpe_ratio, return, volatility, nav"),
    limit: int = Query(10, ge=1, le=100)
):
    """Get top schemes ranked by specified metric"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    unique_schemes = cache.df_features.drop_duplicates('scheme_code', keep='last')
    
    results = []
    
    if metric == "sharpe_ratio":
        unique_schemes = unique_schemes.sort_values('sharpe_ratio_30d', ascending=False, na_position='last')
        for _, row in unique_schemes.head(limit).iterrows():
            results.append({
                'rank': len(results) + 1,
                'scheme_code': int(row['scheme_code']),
                'scheme_name': row['scheme_name'],
                'fund_house': row['fund_house'],
                'value': float(row['sharpe_ratio_30d']) if not pd.isna(row['sharpe_ratio_30d']) else 0.0,
                'unit': 'Sharpe Ratio'
            })
    
    elif metric == "return":
        unique_schemes = unique_schemes.sort_values('cum_return', ascending=False, na_position='last')
        for _, row in unique_schemes.head(limit).iterrows():
            results.append({
                'rank': len(results) + 1,
                'scheme_code': int(row['scheme_code']),
                'scheme_name': row['scheme_name'],
                'fund_house': row['fund_house'],
                'value': float(row['cum_return']) if not pd.isna(row['cum_return']) else 0.0,
                'unit': 'Cumulative Return %'
            })
    
    elif metric == "volatility":
        unique_schemes = unique_schemes.sort_values('volatility_30d', ascending=True, na_position='last')
        for _, row in unique_schemes.head(limit).iterrows():
            results.append({
                'rank': len(results) + 1,
                'scheme_code': int(row['scheme_code']),
                'scheme_name': row['scheme_name'],
                'fund_house': row['fund_house'],
                'value': float(row['volatility_30d']) if not pd.isna(row['volatility_30d']) else 0.0,
                'unit': 'Volatility (30d) %'
            })
    
    elif metric == "nav":
        unique_schemes = unique_schemes.sort_values('net_asset_value', ascending=False)
        for _, row in unique_schemes.head(limit).iterrows():
            results.append({
                'rank': len(results) + 1,
                'scheme_code': int(row['scheme_code']),
                'scheme_name': row['scheme_name'],
                'fund_house': row['fund_house'],
                'value': float(row['net_asset_value']),
                'unit': 'NAV (₹)'
            })
    
    else:
        raise HTTPException(status_code=400, detail="Invalid metric specified")
    
    return {
        'metric': metric,
        'limit': limit,
        'results': results
    }


# ===== ML Endpoints =====
@app.get("/api/ml/clusters", tags=["ML"])
async def get_fund_clusters(
    n_clusters: int = Query(4, ge=2, le=10, description="Number of clusters"),
    random_state: int = Query(42, description="Random seed")
):
    """Cluster schemes by risk/return characteristics"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    scheme_df, summary = cluster_funds(
        cache.df_features,
        n_clusters=n_clusters,
        random_state=random_state
    )

    return {
        "n_clusters": n_clusters,
        "clusters": summary["clusters"],
        "sample": scheme_df.head(50).to_dict(orient="records")
    }


@app.get("/api/ml/rankings", tags=["ML"])
async def get_ml_rankings(
    limit: int = Query(10, ge=1, le=100),
    risk_level: Optional[str] = Query(None, description="LOW, MODERATE, HIGH")
):
    """Rank schemes using multi-factor weighted scoring"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    ranked = rank_funds(cache.df_features, weights=RankingWeights())

    if risk_level:
        risk_upper = risk_level.upper()
        ranked = ranked[ranked["risk_level"] == risk_upper]

    return {
        "limit": limit,
        "results": ranked.head(limit).to_dict(orient="records")
    }


@app.get("/api/ml/recommendations", tags=["ML"])
async def get_ml_recommendations(
    risk_profile: str = Query("moderate", description="low, moderate, high"),
    limit: int = Query(5, ge=1, le=20)
):
    """Recommend schemes based on risk profile"""
    if not cache.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    recommendations = recommend_funds(
        cache.df_features,
        risk_profile=risk_profile,
        top_n=limit,
        config=RecommendationConfig()
    )

    return {
        "risk_profile": risk_profile,
        "limit": limit,
        "results": recommendations.to_dict(orient="records")
    }


# ===== Error Handler =====
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
