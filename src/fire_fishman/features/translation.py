"""Translation gap: tools score vs. production score.

The core question: which prospects have the biggest gap between
their physical tools and their MLB results?
"""

import numpy as np
import pandas as pd


def compute_results_score(batting_stats: pd.DataFrame, player_name: str) -> dict:
    """Extract results metrics from FanGraphs batting stats."""
    player = batting_stats[batting_stats["Name"] == player_name]
    if len(player) == 0:
        return {"woba": np.nan, "wrc_plus": np.nan, "ops": np.nan}

    row = player.iloc[0]
    return {
        "woba": row.get("wOBA", np.nan),
        "wrc_plus": row.get("wRC+", np.nan),
        "ops": row.get("OPS", np.nan),
    }


def compute_translation_gap(
    tools_df: pd.DataFrame,
    results_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute the tools-to-results gap for each prospect.

    A positive gap means tools > results (underperforming tools).
    A negative gap means results > tools (overperforming tools).
    """
    # Both should have batter_id as index
    merged = tools_df.join(results_df, how="inner")

    # Z-score results too (guard against zero variance)
    for col in ["woba", "wrc_plus"]:
        if col in merged.columns:
            std = merged[col].std()
            merged[f"{col}_z"] = (merged[col] - merged[col].mean()) / std if std > 0 else 0.0

    # Gap = tools_z - results_z
    if "tools_composite_z" in merged.columns and "woba_z" in merged.columns:
        merged["translation_gap"] = merged["tools_composite_z"] - merged["woba_z"]

    return merged.sort_values("translation_gap", ascending=False)
