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
    """Barrel rate = barrels / batted ball events."""
    bbe = pitches[
        (pitches["batter"] == batter_id)
        & pitches["launch_speed"].notna()
        & pitches["launch_angle"].notna()
    ]
    if len(bbe) == 0:
        return np.nan

    # Barrel definition (simplified from Statcast):
    # EV >= 98 mph and LA between 26-30, expanding range as EV increases
    barrels = bbe[
        (bbe["launch_speed"] >= 98)
        & (bbe["launch_angle"] >= 26 - (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] <= 30 + (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] >= 8)  # floor
        & (bbe["launch_angle"] <= 50)  # ceiling
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
    """Compute tools scores for a list of batters, then add z-scored composite."""
    records = []
    for bid in batter_ids:
        metrics = compute_tools_score(pitches, bid)
        metrics["batter_id"] = bid
        records.append(metrics)

    df = pd.DataFrame(records).set_index("batter_id")

    # Z-score each metric, then average for composite
    tool_cols = ["avg_exit_velo", "ev90", "barrel_rate", "hard_hit_rate"]
    for col in tool_cols:
        df[f"{col}_z"] = (df[col] - df[col].mean()) / df[col].std()

    z_cols = [f"{c}_z" for c in tool_cols]
    df["tools_composite_z"] = df[z_cols].mean(axis=1)

    return df
