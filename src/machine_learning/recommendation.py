"""Recommendation utilities for mutual fund schemes."""

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from .config import RecommendationConfig
from .feature_prep import FEATURE_COLUMNS, build_scheme_feature_frame


def _risk_lambda(risk_profile: str, config: RecommendationConfig) -> float:
    risk_profile = risk_profile.lower()
    if risk_profile == "low":
        return config.low_risk_lambda
    if risk_profile == "high":
        return config.high_risk_lambda
    return config.moderate_risk_lambda


def _risk_pool(scheme_df: pd.DataFrame, risk_profile: str) -> pd.DataFrame:
    """Filter schemes by the requested risk profile."""
    risk_profile_lower = risk_profile.lower()
    if risk_profile_lower == "low":
        return scheme_df[scheme_df["risk_level"] == "LOW"]
    if risk_profile_lower == "moderate":
        return scheme_df[scheme_df["risk_level"].isin(["LOW", "MODERATE"])]
    return scheme_df


def _profile_anchor(pool: pd.DataFrame) -> pd.DataFrame:
    """Build a centroid vector representing the target investor profile."""
    anchor = pool[FEATURE_COLUMNS].mean(numeric_only=True).to_frame().T
    return anchor.fillna(0.0)


def _apply_utility_score(scheme_df: pd.DataFrame, lambda_risk: float) -> pd.DataFrame:
    """Add a transparent utility score for tie-breaking and explanation."""
    drawdown_penalty = scheme_df["max_drawdown"].abs()

    # Higher return and trend help, while volatility and drawdown reduce score.
    scheme_df["utility_score"] = (
        scheme_df["total_return"]
        - lambda_risk * scheme_df["volatility"]
        + 0.5 * scheme_df["sharpe_ratio"]
        - 0.2 * drawdown_penalty
        + 0.1 * scheme_df["trend_strength"]
    )
    return scheme_df


def recommend_funds(
    df_features: pd.DataFrame,
    risk_profile: str,
    top_n: int = 5,
    config: RecommendationConfig | None = None
) -> pd.DataFrame:
    """Recommend funds by matching a risk-profile centroid with nearest neighbours."""
    config = config or RecommendationConfig()
    scheme_df = build_scheme_feature_frame(df_features)

    # Start from the investor's risk bucket, then fall back to the full universe if needed.
    pool = _risk_pool(scheme_df, risk_profile).copy()
    if pool.empty:
        pool = scheme_df.copy()

    pool = _apply_utility_score(pool, _risk_lambda(risk_profile, config))

    feature_matrix = pool[FEATURE_COLUMNS].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    if feature_matrix.empty:
        return pool.head(top_n).reset_index(drop=True)

    scaler = StandardScaler()
    scaled_matrix = scaler.fit_transform(feature_matrix)

    # Use the mean profile of the selected bucket as the recommendation anchor.
    anchor = _profile_anchor(pool)
    anchor_scaled = scaler.transform(anchor[FEATURE_COLUMNS].replace([np.inf, -np.inf], 0.0).fillna(0.0))

    neighbour_count = min(top_n, len(pool))
    model = NearestNeighbors(n_neighbors=neighbour_count, metric="euclidean")
    model.fit(scaled_matrix)

    distances, indices = model.kneighbors(anchor_scaled)
    recommendations = pool.iloc[indices[0]].copy()
    recommendations["neighbor_distance"] = distances[0]

    recommendations = recommendations.sort_values(
        ["neighbor_distance", "utility_score"],
        ascending=[True, False]
    )

    return recommendations.head(top_n).reset_index(drop=True)
