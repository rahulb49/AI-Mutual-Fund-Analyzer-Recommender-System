"""Clustering utilities for mutual fund schemes."""

from typing import Dict, Tuple
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .config import ClusteringConfig
from .feature_prep import build_scheme_feature_frame, get_feature_matrix


def cluster_funds(
    df_features: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42
) -> Tuple[pd.DataFrame, Dict]:
    """Cluster funds using KMeans on risk/return features."""
    scheme_df = build_scheme_feature_frame(df_features)
    matrix = get_feature_matrix(scheme_df)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    scheme_df["cluster_id"] = model.fit_predict(scaled)

    summary = (
        scheme_df.groupby("cluster_id")
        .agg(
            count=("scheme_code", "count"),
            avg_return=("total_return", "mean"),
            avg_volatility=("volatility", "mean"),
            avg_sharpe=("sharpe_ratio", "mean"),
            avg_drawdown=("max_drawdown", "mean")
        )
        .reset_index()
        .to_dict(orient="records")
    )

    return scheme_df, {"clusters": summary}
