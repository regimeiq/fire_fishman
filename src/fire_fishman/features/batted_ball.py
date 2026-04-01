"""Batted ball direction classification and park factor analysis.

Classifies hit direction (pull/center/oppo) using Statcast hit coordinates
and batter handedness. Identifies short-porch home runs at Yankee Stadium.
"""

import pandas as pd
import numpy as np


# Statcast hit coordinate system: hc_x ~125 is center field.
# Higher hc_x = right field, lower hc_x = left field.
# Pull thresholds based on standard spray chart analysis.
PULL_THRESHOLD_RF = 160   # hc_x > this = right field (LHH pull zone)
PULL_THRESHOLD_LF = 90    # hc_x < this = left field (RHH pull zone)

# Yankee Stadium short porch: 314 ft down RF line, 353 ft to right-center
SHORT_PORCH_MAX_DISTANCE = 370  # ft — anything shorter than this in RF is "short porch" territory


def classify_hit_direction(hc_x: float, stand: str) -> str:
    """Classify a batted ball as pull, center, or oppo.

    Parameters
    ----------
    hc_x : float
        Statcast horizontal hit coordinate (~125 = center field).
    stand : str
        Batter handedness: 'L', 'R', or 'S'.

    Returns
    -------
    str
        'pull', 'center', or 'oppo'.
    """
    if pd.isna(hc_x):
        return np.nan

    if stand == "L":
        # LHH pull = right field (high hc_x)
        if hc_x > PULL_THRESHOLD_RF:
            return "pull"
        elif hc_x < PULL_THRESHOLD_LF:
            return "oppo"
        else:
            return "center"
    else:
        # RHH (and switch) pull = left field (low hc_x)
        if hc_x < PULL_THRESHOLD_LF:
            return "pull"
        elif hc_x > PULL_THRESHOLD_RF:
            return "oppo"
        else:
            return "center"


def classify_hit_directions(df: pd.DataFrame) -> pd.Series:
    """Vectorized hit direction classification for a DataFrame.

    Expects columns: 'hc_x', 'stand'.
    """
    return df.apply(lambda r: classify_hit_direction(r["hc_x"], r["stand"]), axis=1)


def is_short_porch_hr(df: pd.DataFrame) -> pd.Series:
    """Identify home runs that exploited Yankee Stadium's short right field porch.

    Returns boolean Series. True = HR at Yankee Stadium, to right field,
    with distance under SHORT_PORCH_MAX_DISTANCE.
    """
    return (
        (df["home_team"] == "NYY")
        & (df["events"] == "home_run")
        & (df["hc_x"] > PULL_THRESHOLD_RF)
        & (df["hit_distance_sc"] < SHORT_PORCH_MAX_DISTANCE)
    )


def compute_yankee_stadium_hr_splits(pitches: pd.DataFrame) -> pd.DataFrame:
    """Compute HR breakdown at Yankee Stadium by handedness and direction.

    Returns DataFrame with columns: stand, direction, hr_count, avg_exit_velo,
    avg_distance, pct_of_total.
    """
    hrs = pitches[
        (pitches["home_team"] == "NYY")
        & (pitches["events"] == "home_run")
        & pitches["hc_x"].notna()
    ].copy()

    hrs["direction"] = classify_hit_directions(hrs)

    splits = (
        hrs.groupby(["stand", "direction"])
        .agg(
            hr_count=("events", "count"),
            avg_exit_velo=("launch_speed", "mean"),
            avg_distance=("hit_distance_sc", "mean"),
        )
        .reset_index()
    )
    splits["pct_of_total"] = splits["hr_count"] / splits["hr_count"].sum()
    return splits


def compute_park_hr_factor_by_hand(
    pitches: pd.DataFrame, team: str
) -> dict:
    """Compare HR rate for LHH vs RHH at a specific park vs league average.

    Returns dict with LHH and RHH park factors (1.0 = neutral).
    """
    # All batted ball events
    bbe = pitches[pitches["events"].notna()].copy()

    for hand in ["L", "R"]:
        hand_bbe = bbe[bbe["stand"] == hand]
        park_bbe = hand_bbe[hand_bbe["home_team"] == team]
        league_bbe = hand_bbe

        park_hr_rate = (park_bbe["events"] == "home_run").mean()
        league_hr_rate = (league_bbe["events"] == "home_run").mean()

        if hand == "L":
            lhh_factor = park_hr_rate / league_hr_rate if league_hr_rate > 0 else 1.0
        else:
            rhh_factor = park_hr_rate / league_hr_rate if league_hr_rate > 0 else 1.0

    return {"LHH_park_factor": lhh_factor, "RHH_park_factor": rhh_factor}
