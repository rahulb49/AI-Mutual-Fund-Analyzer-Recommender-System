from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class NAVRecord(BaseModel):
    """Data model for a single NAV record from AMFI data"""
    scheme_code: int = Field(..., description="Unique scheme code")
    isin_div_payout: Optional[str] = Field(None, description="ISIN for dividend payout")
    isin_growth: Optional[str] = Field(None, description="ISIN for growth/reinvestment")
    scheme_name: str = Field(..., description="Name of the mutual fund scheme")
    net_asset_value: float = Field(..., description="Net Asset Value (NAV)")
    date: datetime = Field(..., description="NAV date")
    fund_house: Optional[str] = Field(None, description="Fund house/company name")
    
    @validator('scheme_code', pre=True)
    def parse_scheme_code(cls, v):
        """Convert scheme code to integer"""
        if v is None or v == '':
            raise ValueError("Scheme code cannot be empty")
        try:
            return int(v)
        except ValueError:
            raise ValueError(f"Scheme code must be numeric: {v}")
    
    @validator('net_asset_value', pre=True)
    def parse_nav(cls, v):
        """Convert NAV to float"""
        if v is None or v == '' or v == '-':
            raise ValueError("NAV cannot be empty")
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"NAV must be numeric: {v}")
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        """Parse date in DD-MMM-YYYY format"""
        if v is None or v == '' or v == '-':
            raise ValueError("Date cannot be empty")
        try:
            return datetime.strptime(v.strip(), "%d-%b-%Y")
        except ValueError:
            raise ValueError(f"Invalid date format. Expected DD-MMM-YYYY: {v}")
    
    @validator('scheme_name')
    def validate_scheme_name(cls, v):
        """Ensure scheme name is not empty"""
        if not v or not v.strip():
            raise ValueError("Scheme name cannot be empty")
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%d-%b-%Y")
        }


class ParsedNAVData(BaseModel):
    """Container for parsed NAV data with metadata"""
    records: list[NAVRecord]
    total_records: int
    data_date: Optional[datetime] = None
    errors: list[dict] = Field(default_factory=list, description="Parsing errors details")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%d-%b-%Y")
        }


# ===== API Response Schemas =====

class NavMetricsResponse(BaseModel):
    """NAV metrics for a single scheme"""
    scheme_code: int
    scheme_name: str
    fund_house: str
    current_nav: float
    nav_min: float
    nav_max: float
    avg_nav: float


class PerformanceMetricsResponse(BaseModel):
    """Performance metrics for a scheme"""
    total_return: float = Field(..., description="Total return in percentage")
    avg_daily_return: float = Field(..., description="Average daily return")
    best_day: float = Field(..., description="Best daily return")
    worst_day: float = Field(..., description="Worst daily return")
    cumulative_return: float = Field(..., description="Cumulative return")


class RiskMetricsResponse(BaseModel):
    """Risk metrics for a scheme"""
    volatility_30d: float = Field(..., description="30-day annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio (risk-adjusted return)")
    sortino_ratio: float = Field(..., description="Sortino ratio (downside risk-adjusted)")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    risk_level: str = Field(..., description="Risk classification: LOW/MODERATE/HIGH")


class TrendAnalysisResponse(BaseModel):
    """Trend analysis for a scheme"""
    trend_slope: float = Field(..., description="Linear trend slope")
    trend_strength: float = Field(..., description="Trend R² value (0-1)")
    trend_direction: str = Field(..., description="Uptrend/Downtrend/Neutral")
    golden_cross: bool = Field(..., description="SMA_20 > SMA_50 signal")
    price_above_ema: bool = Field(..., description="Price > EMA_12 signal")
    rsi: float = Field(..., description="RSI 14 value")
    rsi_signal: str = Field(..., description="Overbought/Oversold/Neutral")


class SchemeAnalysisResponse(BaseModel):
    """Complete analysis for a scheme"""
    scheme_code: int
    scheme_name: str
    fund_house: str
    nav_metrics: NavMetricsResponse
    performance: PerformanceMetricsResponse
    risk: RiskMetricsResponse
    trend: TrendAnalysisResponse
    data_points: int = Field(..., description="Number of data points used")


class ComparisonSchemeResponse(BaseModel):
    """Simplified scheme data for comparison"""
    scheme_code: int
    scheme_name: str
    fund_house: str
    current_nav: float
    total_return: float
    volatility: float
    sharpe_ratio: float
    risk_level: str


class ComparisonResponse(BaseModel):
    """Comparison of multiple schemes"""
    schemes: list[ComparisonSchemeResponse]
    metric: str = Field(..., description="Comparison metric used")
    sorted_by: str = Field(..., description="Sorting field")


class SearchResponse(BaseModel):
    """Search results for schemes"""
    total_found: int
    schemes: list[dict]
    query: str
    search_field: str


class HealthResponse(BaseModel):
    """API health check response"""
    status: str
    message: str
    timestamp: datetime
    data_loaded: bool


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str
    timestamp: datetime

