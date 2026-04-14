"""Recommendation utilities for mutual fund schemes."""

import pandas as pd

from .config import RecommendationConfig
from .feature_prep import build_scheme_feature_frame


def _risk_lambda(risk_profile: str, config: RecommendationConfig) -> float:
    risk_profile = risk_profile.lower()
    if risk_profile == "low":
        return config.low_risk_lambda
    if risk_profile == "high":
        return config.high_risk_lambda
    return config.moderate_risk_lambda


def recommend_funds(
    df_features: pd.DataFrame,
    risk_profile: str,
    top_n: int = 5,
    config: RecommendationConfig | None = None
) -> pd.DataFrame:
    """Recommend funds based on a risk-adjusted utility score."""
    config = config or RecommendationConfig()
    scheme_df = build_scheme_feature_frame(df_features)

    risk_profile_lower = risk_profile.lower()
    if risk_profile_lower == "low":
        scheme_df = scheme_df[scheme_df["risk_level"] == "LOW"]
    elif risk_profile_lower == "moderate":
        scheme_df = scheme_df[scheme_df["risk_level"].isin(["LOW", "MODERATE"])]

    lambda_risk = _risk_lambda(risk_profile, config)
    drawdown_penalty = scheme_df["max_drawdown"].abs()

    scheme_df["utility_score"] = (
        scheme_df["total_return"]
        - lambda_risk * scheme_df["volatility"]
        + 0.5 * scheme_df["sharpe_ratio"]
        - 0.2 * drawdown_penalty
        + 0.1 * scheme_df["trend_strength"]
    )

    scheme_df = scheme_df.sort_values("utility_score", ascending=False)
    return scheme_df.head(top_n).reset_index(drop=True)
