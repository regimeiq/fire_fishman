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
