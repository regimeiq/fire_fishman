"""Compute physical "tools score" from Statcast data.

Tools score captures raw physical ability independent of results:
exit velocity, bat speed, barrel rate, sprint speed.

These are the metrics that make scouts drool but don't always
translate to MLB production.

All batted-ball metrics are computed over in-play balls (Statcast
``type == "X"``). The raw Statcast feed also records ``launch_speed`` on
roughly half of foul balls; including fouls drags average exit velocity
down by ~5 mph and roughly halves hard-hit rate.
"""

import numpy as np
import pandas as pd


def _batted_balls(pitches: pd.DataFrame, batter_id: int) -> pd.DataFrame:
    """In-play batted balls with a tracked exit velocity for one batter."""
    return pitches[
        (pitches["batter"] == batter_id)
        & (pitches["type"] == "X")
        & pitches["launch_speed"].notna()
    ]


def compute_exit_velo_metrics(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Compute exit velocity metrics for a batter from in-play batted balls."""
    bbe = _batted_balls(pitches, batter_id)

    if len(bbe) == 0:
        return {"avg_exit_velo": np.nan, "ev90": np.nan, "max_exit_velo": np.nan}

    return {
        "avg_exit_velo": bbe["launch_speed"].mean(),
        "ev90": bbe["launch_speed"].quantile(0.90),
        "max_exit_velo": bbe["launch_speed"].max(),
    }


def _is_barrel(bbe: pd.DataFrame) -> pd.Series:
    """Boolean barrel flag for in-play batted balls.

    Uses Statcast's ``launch_speed_angle`` classification (6 = barrel) when
    available. The raw ``statcast()`` feed has no ``barrel`` column, so the
    fallback approximates the Statcast barrel definition from exit velocity
    and launch angle.
    """
    if "launch_speed_angle" in bbe.columns and bbe["launch_speed_angle"].notna().any():
        return bbe["launch_speed_angle"] == 6

    return (
        (bbe["launch_speed"] >= 98)
        & (bbe["launch_angle"] >= 26 - (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] <= 30 + (bbe["launch_speed"] - 98) * 0.5)
        & (bbe["launch_angle"] >= 8)
        & (bbe["launch_angle"] <= 50)
    )


def compute_barrel_rate(pitches: pd.DataFrame, batter_id: int) -> float:
    """Barrel rate = barrels / in-play batted ball events."""
    bbe = _batted_balls(pitches, batter_id)
    bbe = bbe[bbe["launch_angle"].notna()]
    if len(bbe) == 0:
        return np.nan
    return float(_is_barrel(bbe).mean())


def compute_hard_hit_rate(pitches: pd.DataFrame, batter_id: int) -> float:
    """Hard hit rate = in-play batted balls >= 95 mph / total in-play batted balls."""
    bbe = _batted_balls(pitches, batter_id)
    if len(bbe) == 0:
        return np.nan
    return float((bbe["launch_speed"] >= 95).mean())


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
        pitches["batter"].isin(batter_ids)
        & (pitches["type"] == "X")
        & pitches["launch_speed"].notna()
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
        barrel_rate = (
            barrel_bbe.assign(is_barrel=_is_barrel(barrel_bbe))
            .groupby("batter")["is_barrel"]
            .mean()
        )
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
