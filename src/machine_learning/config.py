"""Configuration objects for ML utilities."""

from dataclasses import dataclass


@dataclass
class ClusteringConfig:
    """Configuration for fund clustering."""
    n_clusters: int = 4
    random_state: int = 42


@dataclass
class RankingWeights:
    """Weights for ranking score calculation."""
    return_weight: float = 1.0
    sharpe_weight: float = 0.5
    sortino_weight: float = 0.3
    volatility_weight: float = 0.7
    drawdown_weight: float = 0.4
    trend_weight: float = 0.2


@dataclass
class RecommendationConfig:
    """Configuration for recommendations based on risk profile."""
    low_risk_lambda: float = 2.0
    moderate_risk_lambda: float = 1.0
    high_risk_lambda: float = 0.5
    top_n: int = 5
