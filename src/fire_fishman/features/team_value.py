"""Team value composite: non-offensive contributions to winning.

One canonical definition shared by notebooks 08 and 09:

    pressure = (z(+WPA) + z(-WPA, flipped)) / 2   — high-leverage execution
    hustle   = (z(UBR) + z(BsR)) / 2              — baserunning value
    grit     = z(OAA)                              — fielding outs above average

    value_composite = mean(pressure, hustle, grit)   (equal weights)

Components are z-scored within each season so league-environment shifts do
not dominate. Equal weights are the primary definition — there is no
empirical basis for weighting one component above another.

The batting and fielding tables come from different FanGraphs endpoints that
label teams differently ("NYY" vs "Yankees"), so the merge goes through
``FG_TEAM_NAME_TO_ABBR`` and is validated: a wrong alias silently drops a
team's OAA and shrinks the panel.
"""

import pandas as pd

# FanGraphs team-fielding nickname -> FanGraphs team-batting abbreviation.
# The batting endpoint uses TBR / WSN / CHW (not TB / WSH / CWS).
FG_TEAM_NAME_TO_ABBR = {
    "Angels": "LAA",
    "Astros": "HOU",
    "Athletics": "OAK",
    "Blue Jays": "TOR",
    "Braves": "ATL",
    "Brewers": "MIL",
    "Cardinals": "STL",
    "Cleveland": "CLE",
    "Cubs": "CHC",
    "Diamondbacks": "ARI",
    "Dodgers": "LAD",
    "Giants": "SFG",
    "Guardians": "CLE",
    "Indians": "CLE",
    "Mariners": "SEA",
    "Marlins": "MIA",
    "Mets": "NYM",
    "Nationals": "WSN",
    "Orioles": "BAL",
    "Padres": "SDP",
    "Phillies": "PHI",
    "Pirates": "PIT",
    "Rangers": "TEX",
    "Rays": "TBR",
    "Red Sox": "BOS",
    "Reds": "CIN",
    "Rockies": "COL",
    "Royals": "KCR",
    "Tampa Bay": "TBR",
    "Tigers": "DET",
    "Twins": "MIN",
    "White Sox": "CHW",
    "Yankees": "NYY",
}

# Component -> z-score direction, matching the original notebook definition.
# FanGraphs stores -WPA as a negative total; the -1 direction scores larger
# negative-WPA volume *higher*, so "pressure" indexes how much win-probability
# movement a team generated in both directions (high-leverage involvement)
# rather than net clutch execution. Empirically this keeps the component
# near-orthogonal to wRC+, which is the design goal of the composite;
# z-scoring -WPA with direction +1 would make pressure r ~ +0.8 with wRC+
# (it would just recapture offense).
VALUE_COMPONENTS = {"+WPA": 1, "-WPA": -1, "UBR": 1, "BsR": 1, "OAA": 1}

EQUAL_WEIGHTS = (1 / 3, 1 / 3, 1 / 3)


def merge_team_batting_fielding(
    batting: pd.DataFrame, fielding: pd.DataFrame
) -> pd.DataFrame:
    """Merge FanGraphs team batting and fielding tables on (Season, team).

    Validates the merge instead of silently dropping mismapped teams.
    """
    fielding = fielding.copy()
    fielding["TeamAbbr"] = fielding["Team"].map(FG_TEAM_NAME_TO_ABBR)
    unmapped = fielding.loc[fielding["TeamAbbr"].isna(), "Team"].unique()
    if len(unmapped) > 0:
        raise ValueError(f"Unmapped fielding team labels: {sorted(unmapped)}")

    merged = batting.merge(
        fielding[["Season", "TeamAbbr", "OAA", "DRS"]],
        left_on=["Season", "Team"],
        right_on=["Season", "TeamAbbr"],
        how="left",
    )
    missing = merged.loc[merged["OAA"].isna(), ["Season", "Team"]]
    if len(missing) > 0:
        raise ValueError(
            "Team batting/fielding merge dropped OAA for: "
            f"{missing.to_dict('records')}"
        )
    return merged


def compute_value_composite(
    merged: pd.DataFrame, weights: tuple[float, float, float] = EQUAL_WEIGHTS
) -> pd.DataFrame:
    """Add pressure/hustle/grit components and the value composite.

    Components are z-scored within each season. ``weights`` orders as
    (pressure, hustle, grit) and must sum to 1.
    """
    if abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1, got {weights}")

    frames = []
    for _, season_df in merged.groupby("Season"):
        season_df = season_df.copy()
        for col, direction in VALUE_COMPONENTS.items():
            mean, std = season_df[col].mean(), season_df[col].std()
            season_df[f"{col}_z"] = (
                direction * (season_df[col] - mean) / std if std > 0 else 0.0
            )
        frames.append(season_df)

    df = pd.concat(frames, ignore_index=True)
    df["pressure"] = (df["+WPA_z"] + df["-WPA_z"]) / 2
    df["hustle"] = (df["UBR_z"] + df["BsR_z"]) / 2
    df["grit"] = df["OAA_z"]
    w_p, w_h, w_g = weights
    df["value_composite"] = w_p * df["pressure"] + w_h * df["hustle"] + w_g * df["grit"]
    return df


def build_team_value_df(
    start: int = 2017,
    end: int = 2024,
    weights: tuple[float, float, float] = EQUAL_WEIGHTS,
) -> pd.DataFrame:
    """Load, merge, and score team value for seasons ``start``..``end``.

    Returns one row per team-season with components, ``value_composite``,
    and the underlying FanGraphs batting columns (WAR, wRC+, ...).
    """
    from fire_fishman.data.statcast import get_team_batting_stats, get_team_fielding_stats

    batting = pd.concat(
        [get_team_batting_stats(yr) for yr in range(start, end + 1)], ignore_index=True
    )
    fielding = pd.concat(
        [get_team_fielding_stats(yr) for yr in range(start, end + 1)], ignore_index=True
    )
    merged = merge_team_batting_fielding(batting, fielding)
    return compute_value_composite(merged, weights=weights)
