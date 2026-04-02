"""Statcast data fetching with local parquet caching.

Usage:
    from fire_fishman.data.statcast import get_statcast_pitches, get_batting_stats

    # Pitch-level data for a date range (cached after first pull)
    pitches = get_statcast_pitches(2024)

    # Season-level batting stats from FanGraphs
    batting = get_batting_stats(2024)
"""

from pathlib import Path

import pandas as pd
from pybaseball import cache as pb_cache
from pybaseball import statcast, batting_stats

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Enable pybaseball's internal cache too
pb_cache.enable()


def get_statcast_pitches(season: int, force: bool = False) -> pd.DataFrame:
    """Fetch pitch-level Statcast data for a full season.

    Caches results as parquet. A full season is ~700k rows.
    """
    cache_path = CACHE_DIR / f"statcast_pitches_{season}.parquet"

    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)

    print(f"Pulling Statcast pitch data for {season} (this takes a few minutes)...")
    df = statcast(
        start_dt=f"{season}-03-20",
        end_dt=f"{season}-11-05",
    )
    df.to_parquet(cache_path, index=False)
    print(f"Cached {len(df):,} pitches to {cache_path}")
    return df


def get_batting_stats(season: int, force: bool = False) -> pd.DataFrame:
    """Fetch season-level batting stats from FanGraphs.

    Includes advanced metrics (wOBA, wRC+, etc.) and Statcast aggregates.
    """
    cache_path = CACHE_DIR / f"batting_stats_{season}.parquet"

    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)

    print(f"Pulling FanGraphs batting stats for {season}...")
    df = batting_stats(season, qual=50)  # min 50 PA
    df.to_parquet(cache_path, index=False)
    print(f"Cached {len(df)} player-seasons to {cache_path}")
    return df


def get_statcast_batter(
    player_id: int, start_dt: str, end_dt: str, force: bool = False
) -> pd.DataFrame:
    """Fetch pitch-level data for a specific batter.

    Caches results as parquet keyed on (player_id, start_dt, end_dt).
    """
    from pybaseball import statcast_batter

    cache_path = CACHE_DIR / f"batter_{player_id}_{start_dt}_{end_dt}.parquet"

    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)

    print(f"Pulling Statcast data for batter {player_id} ({start_dt} to {end_dt})...")
    df = statcast_batter(start_dt, end_dt, player_id)
    if len(df) > 0:
        df.to_parquet(cache_path, index=False)
    return df


def get_team_batting_stats(season: int, force: bool = False) -> pd.DataFrame:
    """Fetch team-level batting stats from FanGraphs.

    Includes baserunning (BsR, SB, CS, UBR, wSB, Spd),
    batted ball direction (Pull%, Cent%, Oppo%), and standard offense.
    """
    cache_path = CACHE_DIR / f"team_batting_{season}.parquet"

    if cache_path.exists() and not force:
        return pd.read_parquet(cache_path)

    from pybaseball import team_batting

    print(f"Pulling FanGraphs team batting stats for {season}...")
    df = team_batting(season)
    df.to_parquet(cache_path, index=False)
    print(f"Cached {len(df)} teams to {cache_path}")
    return df


def get_player_id(name: str) -> int:
    """Look up a player's MLBAM ID by name."""
    from pybaseball import playerid_lookup

    last, first = name.split(", ") if ", " in name else (name.split()[-1], name.split()[0])
    result = playerid_lookup(last, first)
    if len(result) == 0:
        raise ValueError(f"No player found for {name}")
    # Return the most recent player (highest key_mlbam)
    return int(result.sort_values("key_mlbam", ascending=False).iloc[0]["key_mlbam"])
