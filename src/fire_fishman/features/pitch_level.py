"""Pitch-level feature engineering for prospect diagnostics.

These features capture HOW a batter interacts with MLB pitching:
chase rate, whiff rate by pitch type, performance by count, etc.

This is where the translation gap lives — tools are physical,
but these features capture decision-making and adaptability.
"""

import numpy as np
import pandas as pd


# Pitch type groupings (Statcast pitch_type codes)
PITCH_GROUPS = {
    "fastball": ["FF", "SI", "FC"],  # 4-seam, sinker, cutter
    "breaking": ["SL", "CU", "KC", "SV", "SC"],  # slider, curve, knuckle-curve, sweeper
    "offspeed": ["CH", "FS", "FO"],  # changeup, splitter, forkball
}


def _classify_pitch(pitch_type: str) -> str:
    """Map Statcast pitch_type to group."""
    for group, codes in PITCH_GROUPS.items():
        if pitch_type in codes:
            return group
    return "other"


def _is_swing(description: str) -> bool:
    """Did the batter swing?"""
    swing_descriptions = [
        "swinging_strike", "swinging_strike_blocked",
        "foul", "foul_tip", "foul_bunt",
        "hit_into_play", "hit_into_play_score", "hit_into_play_no_out",
    ]
    return description in swing_descriptions


def _is_whiff(description: str) -> bool:
    """Did the batter swing and miss?"""
    return description in ["swinging_strike", "swinging_strike_blocked"]


def _is_in_zone(plate_x: float, plate_z: float, sz_top: float, sz_bot: float) -> bool:
    """Is the pitch in the strike zone?"""
    return (-0.83 <= plate_x <= 0.83) and (sz_bot <= plate_z <= sz_top)


def _parse_count(balls: int, strikes: int) -> str:
    """Classify count situation."""
    if strikes == 2:
        return "two_strike"
    if balls >= 2 and strikes <= 1:
        return "hitter_ahead"
    if strikes >= 1 and balls == 0:
        return "pitcher_ahead"
    return "even"


def compute_plate_discipline(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Compute plate discipline metrics for a batter."""
    bp = pitches[pitches["batter"] == batter_id].copy()
    if len(bp) == 0:
        return {}

    bp["in_zone"] = bp.apply(
        lambda r: _is_in_zone(r["plate_x"], r["plate_z"], r["sz_top"], r["sz_bot"])
        if pd.notna(r["plate_x"]) else None,
        axis=1,
    )
    bp["is_swing"] = bp["description"].apply(_is_swing)
    bp["is_whiff"] = bp["description"].apply(_is_whiff)

    in_zone = bp[bp["in_zone"] == True]
    out_zone = bp[bp["in_zone"] == False]
    swings = bp[bp["is_swing"]]

    return {
        "chase_rate": out_zone["is_swing"].mean() if len(out_zone) > 0 else np.nan,
        "zone_swing_rate": in_zone["is_swing"].mean() if len(in_zone) > 0 else np.nan,
        "zone_contact_rate": (
            1 - in_zone[in_zone["is_swing"]]["is_whiff"].mean()
            if len(in_zone[in_zone["is_swing"]]) > 0 else np.nan
        ),
        "whiff_rate": swings["is_whiff"].mean() if len(swings) > 0 else np.nan,
        "total_pitches_seen": len(bp),
    }


def compute_whiff_by_pitch_type(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Whiff rate broken down by pitch group (fastball, breaking, offspeed)."""
    bp = pitches[pitches["batter"] == batter_id].copy()
    bp["pitch_group"] = bp["pitch_type"].apply(_classify_pitch)
    bp["is_swing"] = bp["description"].apply(_is_swing)
    bp["is_whiff"] = bp["description"].apply(_is_whiff)

    results = {}
    for group in ["fastball", "breaking", "offspeed"]:
        group_swings = bp[(bp["pitch_group"] == group) & bp["is_swing"]]
        results[f"whiff_rate_{group}"] = (
            group_swings["is_whiff"].mean() if len(group_swings) > 0 else np.nan
        )
        results[f"chase_rate_{group}"] = np.nan
        out_zone = bp[(bp["pitch_group"] == group)]
        if "plate_x" in bp.columns:
            out_zone = out_zone[
                out_zone.apply(
                    lambda r: not _is_in_zone(r["plate_x"], r["plate_z"], r["sz_top"], r["sz_bot"])
                    if pd.notna(r["plate_x"]) else False,
                    axis=1,
                )
            ]
            if len(out_zone) > 0:
                results[f"chase_rate_{group}"] = out_zone["is_swing"].mean()

    return results


def compute_count_performance(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Performance splits by count situation."""
    bp = pitches[pitches["batter"] == batter_id].copy()
    bp["is_whiff"] = bp["description"].apply(_is_whiff)
    bp["is_swing"] = bp["description"].apply(_is_swing)
    bp["count_situation"] = bp.apply(lambda r: _parse_count(r["balls"], r["strikes"]), axis=1)

    results = {}
    for situation in ["two_strike", "hitter_ahead", "pitcher_ahead", "even"]:
        sit_pitches = bp[bp["count_situation"] == situation]
        sit_swings = sit_pitches[sit_pitches["is_swing"]]
        results[f"whiff_rate_{situation}"] = (
            sit_swings["is_whiff"].mean() if len(sit_swings) > 0 else np.nan
        )

    return results


def compute_velo_tier_performance(pitches: pd.DataFrame, batter_id: int) -> dict:
    """How does the batter perform vs. different velocity tiers?"""
    bp = pitches[
        (pitches["batter"] == batter_id)
        & pitches["release_speed"].notna()
    ].copy()
    bp["is_swing"] = bp["description"].apply(_is_swing)
    bp["is_whiff"] = bp["description"].apply(_is_whiff)

    bp["velo_tier"] = pd.cut(
        bp["release_speed"],
        bins=[0, 90, 93, 96, 110],
        labels=["soft_sub90", "avg_90_93", "hard_93_96", "elite_96plus"],
    )

    results = {}
    for tier in ["soft_sub90", "avg_90_93", "hard_93_96", "elite_96plus"]:
        tier_swings = bp[(bp["velo_tier"] == tier) & bp["is_swing"]]
        results[f"whiff_rate_{tier}"] = (
            tier_swings["is_whiff"].mean() if len(tier_swings) > 0 else np.nan
        )
        # Also compute xwOBA proxy: contact quality when they do hit it
        tier_contact = bp[
            (bp["velo_tier"] == tier) & bp["launch_speed"].notna()
        ]
        results[f"avg_ev_{tier}"] = (
            tier_contact["launch_speed"].mean() if len(tier_contact) > 0 else np.nan
        )

    return results


def compute_all_pitch_features(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Compute all pitch-level features for a batter."""
    features = {}
    features.update(compute_plate_discipline(pitches, batter_id))
    features.update(compute_whiff_by_pitch_type(pitches, batter_id))
    features.update(compute_count_performance(pitches, batter_id))
    features.update(compute_velo_tier_performance(pitches, batter_id))
    return features


def compute_pitch_features_for_cohort(
    pitches: pd.DataFrame, batter_ids: list[int]
) -> pd.DataFrame:
    """Compute pitch-level features for a list of batters."""
    records = []
    for bid in batter_ids:
        features = compute_all_pitch_features(pitches, bid)
        features["batter_id"] = bid
        records.append(features)
    return pd.DataFrame(records).set_index("batter_id")
