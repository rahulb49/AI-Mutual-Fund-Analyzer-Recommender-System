"""Feature preparation helpers for ML models."""

from typing import List
import pandas as pd
import numpy as np


FEATURE_COLUMNS: List[str] = [
    "total_return",
    "volatility",
    "sharpe_ratio",
    "sortino_ratio",
    "max_drawdown",
    "trend_strength",
]


def _coalesce_column(df: pd.DataFrame, target: str, source: str) -> None:
    """Copy a source column to a target if present, otherwise fill with zeros."""
    if source in df.columns:
        df[target] = pd.to_numeric(df[source], errors="coerce").fillna(0.0)
    else:
        df[target] = 0.0


def build_scheme_feature_frame(df_features: pd.DataFrame) -> pd.DataFrame:
    """Build a scheme-level feature table from time-series features."""
    df = df_features.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date")

    latest = df.drop_duplicates("scheme_code", keep="last").copy()

    _coalesce_column(latest, "total_return", "cum_return")
    _coalesce_column(latest, "volatility", "volatility_30d")
    _coalesce_column(latest, "sharpe_ratio", "sharpe_ratio_30d")
    _coalesce_column(latest, "sortino_ratio", "sortino_ratio_30d")
    _coalesce_column(latest, "max_drawdown", "max_drawdown_1y")
    _coalesce_column(latest, "trend_strength", "trend_strength")

    latest["risk_level"] = np.where(
        latest["volatility"] < 5,
        "LOW",
        np.where(latest["volatility"] < 15, "MODERATE", "HIGH")
    )

    return latest[
        [
            "scheme_code",
            "scheme_name",
            "fund_house",
            "total_return",
            "volatility",
            "sharpe_ratio",
            "sortino_ratio",
            "max_drawdown",
            "trend_strength",
            "risk_level",
        ]
    ].reset_index(drop=True)


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return numeric feature matrix used for modeling."""
    return df[FEATURE_COLUMNS].replace([np.inf, -np.inf], 0.0).fillna(0.0)
