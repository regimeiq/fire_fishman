"""Top prospect data: player IDs, rankings, and call-up dates.

Manually curated list of top-100 prospects who debuted 2019-2024,
with their MLBAM IDs for Statcast lookups.

Sources: Baseball America, FanGraphs, MLB Pipeline rankings.
"""

import pandas as pd

# fmt: off
# Top prospects who debuted 2019-2024 with meaningful MLB time
# Columns: name, mlbam_id, debut_year, pre_debut_rank (approximate BA/FG top-100 rank)
# "outcome": rough classification based on first 2 MLB seasons
#   - "star": >= .340 wOBA in years 1-2
#   - "solid": .310-.340 wOBA
#   - "disappointing": .280-.310 wOBA
#   - "bust": < .280 wOBA (or didn't stick)
PROSPECT_DATA = [
    # === Yankees focus ===
    ("Anthony Volpe",       683011, 2023, 5,  "disappointing"),
    ("Jasson Dominguez",    691176, 2023, 15, "disappointing"),

    # === Stars (tools converted) ===
    ("Julio Rodriguez",     677594, 2022, 1,  "star"),
    ("Bobby Witt Jr.",      677951, 2022, 1,  "star"),
    ("Gunnar Henderson",    683002, 2022, 2,  "star"),
    ("Corbin Carroll",      682998, 2022, 3,  "star"),
    ("Adley Rutschman",     668939, 2022, 1,  "star"),
    ("Riley Greene",        682985, 2022, 10, "star"),
    ("CJ Abrams",          682928, 2022, 8,  "solid"),
    ("Elly De La Cruz",    682829, 2023, 3,  "star"),
    ("Jackson Chourio",    694192, 2024, 1,  "solid"),
    ("Marcelo Mayer",      691606, 2024, 3,  "solid"),

    # === Disappointing (tools present, results lagging) ===
    ("Spencer Torkelson",   669060, 2022, 3,  "disappointing"),
    ("Nolan Jones",         666134, 2022, 40, "solid"),
    ("Jordyn Adams",        677941, 2023, 50, "bust"),
    ("Josh Jung",           673962, 2022, 8,  "solid"),
    ("Ezequiel Tovar",     678545, 2022, 20, "solid"),
    ("Jordan Walker",      691007, 2023, 2,  "disappointing"),
    ("Matt McLain",        680757, 2023, 12, "solid"),
    ("Brooks Lee",         700362, 2024, 10, "disappointing"),

    # === Busts (elite tools, didn't translate) ===
    ("Joey Bart",           663698, 2020, 15, "bust"),
    ("Jarred Kelenic",      672284, 2021, 4,  "bust"),
    ("Nick Madrigal",       663611, 2020, 15, "disappointing"),
]
# fmt: on


def get_prospect_df() -> pd.DataFrame:
    """Return prospect data as a DataFrame."""
    df = pd.DataFrame(
        PROSPECT_DATA,
        columns=["name", "mlbam_id", "debut_year", "pre_debut_rank", "outcome"],
    )
    return df


def get_prospect_ids() -> dict[str, int]:
    """Return {name: mlbam_id} mapping for all tracked prospects."""
    return {name: mid for name, mid, *_ in PROSPECT_DATA}


def get_yankees_prospects() -> pd.DataFrame:
    """Return just the Yankees prospects."""
    df = get_prospect_df()
    return df[df["name"].isin(["Anthony Volpe", "Jasson Dominguez"])]


# MiLB season-level stats (from FanGraphs/Baseball Reference)
# Not available via pybaseball API — manually sourced from public pages.
MILB_STATS = {
    "Anthony Volpe": {
        2021: {"level": "A/A+", "pa": 514, "avg": .294, "obp": .423, "slg": .604,
               "hr": 27, "sb": 33, "bb_pct": .148, "k_pct": .253,
               "note": "BA Best Strike-Zone Discipline in Yankees system"},
        2022: {"level": "AA/AAA", "pa": 576, "avg": .249, "obp": .341, "slg": .431,
               "hr": 21, "sb": 50, "bb_pct": .113, "k_pct": .248,
               "note": "65 BB in 132 games"},
    },
    "Jasson Dominguez": {
        2022: {"level": "A+", "pa": 330, "avg": .265, "obp": .351, "slg": .453,
               "hr": 9, "sb": 19, "k_pct": .230,
               "note": "75 games with Tampa"},
        2023: {"level": "AA/AAA", "pa": 194, "avg": .372, "obp": .442, "slg": .557,
               "hr": 5, "sb": 7, "k_pct": .173,
               "note": "BA Best Strike-Zone Discipline; 44 games before call-up"},
    },
    # Additional Yankees system products for systemic comparison
    "Oswald Peraza": {
        2022: {"level": "AAA", "pa": 480, "avg": .259, "obp": .316, "slg": .399,
               "hr": 12, "sb": 33, "k_pct": .209},
    },
}


# Yankees system prospects (expanded for systemic analysis)
YANKEES_SYSTEM = [
    ("Anthony Volpe",       683011, 2023, 5,  "disappointing"),
    ("Jasson Dominguez",    691176, 2023, 15, "disappointing"),
    ("Oswald Peraza",       672724, 2022, 20, "bust"),
    ("Everson Pereira",     676633, 2024, 80, "bust"),
    ("Austin Wells",        670770, 2023, 25, "solid"),
    ("Ben Rice",            700892, 2024, 50, "disappointing"),
]


def get_yankees_system_df() -> pd.DataFrame:
    """Return all Yankees system products for systemic analysis."""
    return pd.DataFrame(
        YANKEES_SYSTEM,
        columns=["name", "mlbam_id", "debut_year", "pre_debut_rank", "outcome"],
    )
