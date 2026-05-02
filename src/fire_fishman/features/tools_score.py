"""Compute physical "tools score" from Statcast data.

Tools score captures raw physical ability independent of results:
exit velocity, bat speed, barrel rate, sprint speed.

These are the metrics that make scouts drool but don't always
translate to MLB production.
"""

import numpy as np
import pandas as pd


def compute_exit_velo_metrics(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Compute exit velocity metrics for a batter from pitch-level data."""
    batter_pitches = pitches[
        (pitches["batter"] == batter_id) & pitches["launch_speed"].notna()
    ]

    if len(batter_pitches) == 0:
        return {"avg_exit_velo": np.nan, "ev90": np.nan, "max_exit_velo": np.nan}

    return {
        "avg_exit_velo": batter_pitches["launch_speed"].mean(),
        "ev90": batter_pitches["launch_speed"].quantile(0.90),
        "max_exit_velo": batter_pitches["launch_speed"].max(),
    }


def compute_barrel_rate(pitches: pd.DataFrame, batter_id: int) -> float:
    """Barrel rate = barrels / batted ball events.

    Uses Statcast's native barrel classification when available,
    falls back to an approximation otherwise.
    """
    bbe = pitches[
        (pitches["batter"] == batter_id)
        & pitches["launch_speed"].notna()
        & pitches["launch_angle"].notna()
    ]
    if len(bbe) == 0:
        return np.nan

    # Prefer Statcast's own barrel flag if present
    if "barrel" in bbe.columns:
        return bbe["barrel"].fillna(0).astype(bool).mean()

    # Fallback: approximation of Statcast barrel definition
    barrels = bbe[
        (bbe["launch_speed"] >= 98)
        & (bbe["launch_angle"] >= 26 - (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] <= 30 + (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] >= 8)
        & (bbe["launch_angle"] <= 50)
    ]
    return len(barrels) / len(bbe)


def compute_hard_hit_rate(pitches: pd.DataFrame, batter_id: int) -> float:
    """Hard hit rate = batted balls >= 95 mph / total batted balls."""
    bbe = pitches[
        (pitches["batter"] == batter_id) & pitches["launch_speed"].notna()
    ]
    if len(bbe) == 0:
        return np.nan
    return (bbe["launch_speed"] >= 95).mean()


def compute_tools_score(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Compute all tool metrics for a batter.

    Returns a dict of raw metrics plus a composite z-score
    (to be computed across the full prospect cohort).
    """
    ev_metrics = compute_exit_velo_metrics(pitches, batter_id)
    barrel = compute_barrel_rate(pitches, batter_id)
    hard_hit = compute_hard_hit_rate(pitches, batter_id)

    return {
        **ev_metrics,
        "barrel_rate": barrel,
        "hard_hit_rate": hard_hit,
    }


def compute_tools_for_cohort(pitches: pd.DataFrame, batter_ids: list[int]) -> pd.DataFrame:
    """Compute tools scores for a list of batters, then add z-scored composite.

    Uses one filtered pass over the pitch table instead of rescanning it once per
    batter/metric.
    """
    index = pd.Index(batter_ids, name="batter_id")
    bbe = pitches[
        pitches["batter"].isin(batter_ids) & pitches["launch_speed"].notna()
    ].copy()

    df = pd.DataFrame(index=index)
    if len(bbe) > 0:
        grouped = bbe.groupby("batter")["launch_speed"]
        df["avg_exit_velo"] = grouped.mean().reindex(index)
        df["ev90"] = grouped.quantile(0.90).reindex(index)
        df["max_exit_velo"] = grouped.max().reindex(index)
        df["hard_hit_rate"] = (
            bbe.assign(hard_hit=bbe["launch_speed"] >= 95)
            .groupby("batter")["hard_hit"]
            .mean()
            .reindex(index)
        )

        barrel_bbe = bbe[bbe["launch_angle"].notna()].copy()
        if "barrel" in barrel_bbe.columns:
            barrel_rate = barrel_bbe.assign(
                is_barrel=barrel_bbe["barrel"].fillna(0).astype(bool)
            ).groupby("batter")["is_barrel"].mean()
        else:
            barrel_angle_min = 26 - (barrel_bbe["launch_speed"] - 98) * 0.5
            barrel_angle_max = 30 + (barrel_bbe["launch_speed"] - 98) * 0.5
            barrel_rate = barrel_bbe.assign(
                is_barrel=(
                    (barrel_bbe["launch_speed"] >= 98)
                    & (barrel_bbe["launch_angle"] >= barrel_angle_min)
                    & (barrel_bbe["launch_angle"] <= barrel_angle_max)
                    & (barrel_bbe["launch_angle"] >= 8)
                    & (barrel_bbe["launch_angle"] <= 50)
                )
            ).groupby("batter")["is_barrel"].mean()
        df["barrel_rate"] = barrel_rate.reindex(index)
    else:
        df[["avg_exit_velo", "ev90", "max_exit_velo", "barrel_rate", "hard_hit_rate"]] = np.nan

    # Z-score each metric, then average for composite
    tool_cols = ["avg_exit_velo", "ev90", "barrel_rate", "hard_hit_rate"]
    for col in tool_cols:
        std = df[col].std()
        df[f"{col}_z"] = (df[col] - df[col].mean()) / std if pd.notna(std) and std > 0 else 0.0

    z_cols = [f"{c}_z" for c in tool_cols]
    df["tools_composite_z"] = df[z_cols].mean(axis=1)

    return df
