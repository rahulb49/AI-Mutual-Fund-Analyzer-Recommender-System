"""Ranking utilities for mutual fund schemes."""

import pandas as pd
import numpy as np

from .config import RankingWeights
from .feature_prep import build_scheme_feature_frame


def rank_funds(
    df_features: pd.DataFrame,
    weights: RankingWeights | None = None
) -> pd.DataFrame:
    """Rank funds using a weighted multi-factor score."""
    scheme_df = build_scheme_feature_frame(df_features)
    weights = weights or RankingWeights()

    drawdown_penalty = scheme_df["max_drawdown"].abs()

    scheme_df["score"] = (
        weights.return_weight * scheme_df["total_return"]
        + weights.sharpe_weight * scheme_df["sharpe_ratio"]
        + weights.sortino_weight * scheme_df["sortino_ratio"]
        - weights.volatility_weight * scheme_df["volatility"]
        - weights.drawdown_weight * drawdown_penalty
        + weights.trend_weight * scheme_df["trend_strength"]
    )

    scheme_df["rank"] = scheme_df["score"].rank(ascending=False, method="dense").astype(int)
    scheme_df = scheme_df.sort_values(["rank", "scheme_code"]).reset_index(drop=True)

    return scheme_df
