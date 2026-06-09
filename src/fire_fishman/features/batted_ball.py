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


def classify_hit_directions(df: pd.DataFrame) -> pd.Series:
    """Vectorized hit direction classification for a DataFrame.

    Expects columns: 'hc_x', 'stand'.
    """
    hc_x = df["hc_x"]
    stand = df["stand"]

    # LHH: pull = RF (high hc_x), oppo = LF (low hc_x)
    # RHH/S: pull = LF (low hc_x), oppo = RF (high hc_x)
    is_lhh = stand == "L"

    pull = (is_lhh & (hc_x > PULL_THRESHOLD_RF)) | (~is_lhh & (hc_x < PULL_THRESHOLD_LF))
    oppo = (is_lhh & (hc_x < PULL_THRESHOLD_LF)) | (~is_lhh & (hc_x > PULL_THRESHOLD_RF))

    result = pd.Series("center", index=df.index)
    result[pull] = "pull"
    result[oppo] = "oppo"
    result[hc_x.isna()] = np.nan
    return result


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
    total_hrs = splits["hr_count"].sum()
    splits["pct_of_total"] = splits["hr_count"] / total_hrs if total_hrs > 0 else np.nan
    return splits
