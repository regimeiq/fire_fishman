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


SWING_DESCRIPTIONS = frozenset([
    "swinging_strike", "swinging_strike_blocked",
    "foul", "foul_tip", "foul_bunt",
    "hit_into_play", "hit_into_play_score", "hit_into_play_no_out",
])

WHIFF_DESCRIPTIONS = frozenset(["swinging_strike", "swinging_strike_blocked"])


def _is_swing(description: str) -> bool:
    """Did the batter swing?"""
    return description in SWING_DESCRIPTIONS


def _is_whiff(description: str) -> bool:
    """Did the batter swing and miss?"""
    return description in WHIFF_DESCRIPTIONS


def _is_in_zone(plate_x: float, plate_z: float, sz_top: float, sz_bot: float) -> bool:
    """Is the pitch in the strike zone?"""
    return (-0.83 <= plate_x <= 0.83) and (sz_bot <= plate_z <= sz_top)


def _vectorized_zone_swing_whiff(bp: pd.DataFrame) -> pd.DataFrame:
    """Add in_zone, is_swing, is_whiff columns using vectorized operations."""
    bp = bp.copy()
    bp["in_zone"] = (
        bp["plate_x"].between(-0.83, 0.83)
        & bp["plate_z"].between(bp["sz_bot"], bp["sz_top"])
        & bp["plate_x"].notna()
    )
    bp["is_swing"] = bp["description"].isin(SWING_DESCRIPTIONS)
    bp["is_whiff"] = bp["description"].isin(WHIFF_DESCRIPTIONS)
    bp["pitch_group"] = bp["pitch_type"].map(
        {code: group for group, codes in PITCH_GROUPS.items() for code in codes}
    ).fillna("other")
    return bp


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
    bp = pitches[pitches["batter"] == batter_id]
    if len(bp) == 0:
        return {}

    bp = _vectorized_zone_swing_whiff(bp)

    in_zone = bp[bp["in_zone"]]
    out_zone = bp[~bp["in_zone"] & bp["plate_x"].notna()]
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
    bp = pitches[pitches["batter"] == batter_id]
    bp = _vectorized_zone_swing_whiff(bp)

    results = {}
    for group in ["fastball", "breaking", "offspeed"]:
        group_pitches = bp[bp["pitch_group"] == group]
        group_swings = group_pitches[group_pitches["is_swing"]]
        results[f"whiff_rate_{group}"] = (
            group_swings["is_whiff"].mean() if len(group_swings) > 0 else np.nan
        )
        out_zone = group_pitches[~group_pitches["in_zone"] & group_pitches["plate_x"].notna()]
        results[f"chase_rate_{group}"] = (
            out_zone["is_swing"].mean() if len(out_zone) > 0 else np.nan
        )

    return results


def compute_count_performance(pitches: pd.DataFrame, batter_id: int) -> dict:
    """Performance splits by count situation."""
    bp = pitches[pitches["batter"] == batter_id].copy()
    bp["is_whiff"] = bp["description"].isin(WHIFF_DESCRIPTIONS)
    bp["is_swing"] = bp["description"].isin(SWING_DESCRIPTIONS)
    bp["count_situation"] = np.select(
        [
            bp["strikes"] == 2,
            (bp["balls"] >= 2) & (bp["strikes"] <= 1),
            (bp["strikes"] >= 1) & (bp["balls"] == 0),
        ],
        ["two_strike", "hitter_ahead", "pitcher_ahead"],
        default="even",
    )

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
    bp["is_swing"] = bp["description"].isin(SWING_DESCRIPTIONS)
    bp["is_whiff"] = bp["description"].isin(WHIFF_DESCRIPTIONS)

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
    """Compute pitch-level features for a list of batters.

    Pre-filters the DataFrame once to avoid repeated full-table scans.
    """
    filtered = pitches[pitches["batter"].isin(batter_ids)]
    records = []
    for bid in batter_ids:
        features = compute_all_pitch_features(filtered, bid)
        features["batter_id"] = bid
        records.append(features)
    return pd.DataFrame(records).set_index("batter_id")


def compute_monthly_discipline(
    pitches: pd.DataFrame, batter_id: int, min_pitches: int = 50
) -> pd.DataFrame:
    """Monthly plate discipline metrics for trajectory analysis.

    Returns one row per (year, month) with chase rate, whiff rate,
    breaking ball chase, offspeed chase, zone contact, and 96+ whiff.
    Months with fewer than *min_pitches* are excluded.
    """
    bp = pitches[pitches["batter"] == batter_id].copy()
    if len(bp) == 0:
        return pd.DataFrame()

    bp["game_date"] = pd.to_datetime(bp["game_date"])
    bp["year"] = bp["game_date"].dt.year
    bp["month"] = bp["game_date"].dt.month
    bp = _vectorized_zone_swing_whiff(bp)

    records = []
    for (year, month), mp in bp.groupby(["year", "month"]):
        if len(mp) < min_pitches:
            continue
        oz = mp[mp["in_zone"] == False]
        iz = mp[mp["in_zone"] == True]
        swings = mp[mp["is_swing"]]
        brk_oz = mp[(mp["pitch_group"] == "breaking") & (mp["in_zone"] == False)]
        off_oz = mp[(mp["pitch_group"] == "offspeed") & (mp["in_zone"] == False)]
        velo96 = mp[(mp["release_speed"] >= 96) & mp["is_swing"]]
        iz_swings = iz[iz["is_swing"]]

        records.append({
            "year": int(year),
            "month": int(month),
            "n_pitches": len(mp),
            "chase_rate": oz["is_swing"].mean() if len(oz) > 0 else np.nan,
            "whiff_rate": swings["is_whiff"].mean() if len(swings) > 0 else np.nan,
            "brk_chase": brk_oz["is_swing"].mean() if len(brk_oz) > 0 else np.nan,
            "off_chase": off_oz["is_swing"].mean() if len(off_oz) > 0 else np.nan,
            "zone_contact": (
                1 - iz_swings["is_whiff"].mean() if len(iz_swings) > 0 else np.nan
            ),
            "velo96_whiff": velo96["is_whiff"].mean() if len(velo96) > 0 else np.nan,
        })
    return pd.DataFrame(records)


def compute_yearly_discipline(
    pitches: pd.DataFrame, batter_id: int
) -> pd.DataFrame:
    """Season-level discipline metrics aggregated from pitch data."""
    bp = pitches[pitches["batter"] == batter_id].copy()
    if len(bp) == 0:
        return pd.DataFrame()

    bp["game_date"] = pd.to_datetime(bp["game_date"])
    bp["year"] = bp["game_date"].dt.year
    bp = _vectorized_zone_swing_whiff(bp)

    records = []
    for year, yp in bp.groupby("year"):
        oz = yp[yp["in_zone"] == False]
        iz = yp[yp["in_zone"] == True]
        swings = yp[yp["is_swing"]]
        brk_oz = yp[(yp["pitch_group"] == "breaking") & (yp["in_zone"] == False)]
        off_oz = yp[(yp["pitch_group"] == "offspeed") & (yp["in_zone"] == False)]
        velo96 = yp[(yp["release_speed"] >= 96) & yp["is_swing"]]
        iz_swings = iz[iz["is_swing"]]

        records.append({
            "year": int(year),
            "n_pitches": len(yp),
            "chase_rate": oz["is_swing"].mean() if len(oz) > 0 else np.nan,
            "whiff_rate": swings["is_whiff"].mean() if len(swings) > 0 else np.nan,
            "brk_chase": brk_oz["is_swing"].mean() if len(brk_oz) > 0 else np.nan,
            "off_chase": off_oz["is_swing"].mean() if len(off_oz) > 0 else np.nan,
            "zone_contact": (
                1 - iz_swings["is_whiff"].mean() if len(iz_swings) > 0 else np.nan
            ),
            "velo96_whiff": velo96["is_whiff"].mean() if len(velo96) > 0 else np.nan,
        })
    return pd.DataFrame(records)
