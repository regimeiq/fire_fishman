"""Top prospect data: player IDs, rankings, and call-up dates.

Manually curated list of top-100 prospects who debuted 2019-2024,
with their MLBAM IDs for Statcast lookups.

Sources: Baseball America, FanGraphs, MLB Pipeline rankings.
"""

import pandas as pd

# fmt: off
# Top prospects who debuted 2019-2024 with meaningful MLB time
# Columns: name, mlbam_id, debut_year, pre_debut_rank, outcome, org
# "outcome": rough classification based on first 2 MLB seasons
#   - "star": >= .340 wOBA in years 1-2
#   - "solid": .310-.340 wOBA
#   - "disappointing": .280-.310 wOBA
#   - "bust": < .280 wOBA (or didn't stick)
# "org": organization that developed the player (not necessarily current team)
PROSPECT_DATA = [
    # === Yankees ===
    ("Anthony Volpe",       683011, 2023, 5,  "disappointing", "NYY"),
    ("Jasson Dominguez",    691176, 2023, 15, "disappointing", "NYY"),
    ("Ben Rice",            700250, 2024, 50, "solid",         "NYY"),
    ("Oswald Peraza",       672724, 2022, 20, "bust",          "NYY"),
    ("Everson Pereira",     676633, 2024, 80, "bust",          "NYY"),
    ("Austin Wells",        670770, 2023, 25, "solid",         "NYY"),

    # === Baltimore — elite development org ===
    ("Gunnar Henderson",    683002, 2022, 2,  "star",          "BAL"),
    ("Adley Rutschman",     668939, 2022, 1,  "star",          "BAL"),
    ("Colton Cowser",       681297, 2024, 25, "solid",         "BAL"),
    ("Heston Kjerstad",     677008, 2024, 40, "solid",         "BAL"),
    ("Jordan Westburg",     676059, 2023, 30, "solid",         "BAL"),

    # === Cleveland — elite development org ===
    ("Nolan Jones",         666134, 2022, 40, "solid",         "CLE"),
    ("Steven Kwan",         680757, 2022, 50, "star",          "CLE"),
    ("Bo Naylor",           666310, 2022, 35, "solid",         "CLE"),
    ("Tyler Freeman",       671289, 2022, 45, "disappointing", "CLE"),
    ("Brayan Rocchio",      677587, 2023, 60, "disappointing", "CLE"),

    # === Los Angeles Dodgers — elite development org ===
    ("Andy Pages",          681624, 2024, 30, "solid",         "LAD"),
    ("James Outman",        681546, 2023, 35, "solid",         "LAD"),
    ("Miguel Vargas",       678246, 2022, 20, "disappointing", "LAD"),

    # === Tampa Bay — elite development org ===
    ("Josh Lowe",           666139, 2022, 25, "solid",         "TB"),
    ("Curtis Mead",         678554, 2024, 20, "disappointing", "TB"),
    ("Junior Caminero",     691406, 2023, 5,  "disappointing", "TB"),

    # === Atlanta — elite development org ===
    ("Michael Harris II",   671739, 2022, 10, "star",          "ATL"),
    ("Vaughn Grissom",      687093, 2022, 35, "disappointing", "ATL"),
    ("Cristian Pache",      665506, 2020, 11, "bust",          "ATL"),

    # === Other orgs (comparison cohort) ===
    ("Julio Rodriguez",     677594, 2022, 1,  "star",          "SEA"),
    ("Bobby Witt Jr.",      677951, 2022, 1,  "star",          "KC"),
    ("Corbin Carroll",      682998, 2022, 3,  "star",          "ARI"),
    ("Riley Greene",        682985, 2022, 10, "star",          "DET"),
    ("CJ Abrams",          682928, 2022, 8,  "solid",         "SD"),
    ("Elly De La Cruz",    682829, 2023, 3,  "star",          "CIN"),
    ("Jackson Chourio",    694192, 2024, 1,  "solid",         "MIL"),
    ("Marcelo Mayer",      691606, 2024, 3,  "solid",         "BOS"),
    ("Spencer Torkelson",   669060, 2022, 3,  "disappointing", "DET"),
    ("Jordyn Adams",        677941, 2023, 50, "bust",          "LAA"),
    ("Josh Jung",           673962, 2022, 8,  "solid",         "TEX"),
    ("Ezequiel Tovar",     678545, 2022, 20, "solid",         "COL"),
    ("Jordan Walker",      691007, 2023, 2,  "disappointing", "STL"),
    ("Matt McLain",        680574, 2023, 12, "solid",         "CIN"),
    ("Brooks Lee",         700362, 2024, 10, "disappointing", "MIN"),
    ("Joey Bart",           663698, 2020, 15, "bust",          "SF"),
    ("Jarred Kelenic",      672284, 2021, 4,  "bust",          "SEA"),
    ("Nick Madrigal",       663611, 2020, 15, "disappointing", "CHW"),
]
# fmt: on

# Target organizations for the development pipeline comparison
ELITE_DEV_ORGS = ("BAL", "CLE", "LAD", "TB", "ATL")
TARGET_ORGS = ("NYY",) + ELITE_DEV_ORGS


def get_prospect_df() -> pd.DataFrame:
    """Return prospect data as a DataFrame."""
    df = pd.DataFrame(
        PROSPECT_DATA,
        columns=["name", "mlbam_id", "debut_year", "pre_debut_rank", "outcome", "org"],
    )
    return df


def get_prospect_ids() -> dict[str, int]:
    """Return {name: mlbam_id} mapping for all tracked prospects."""
    return {name: mid for name, mid, *_ in PROSPECT_DATA}


def get_yankees_prospects() -> pd.DataFrame:
    """Return just the core Yankees prospects (Volpe, Dominguez, Rice)."""
    df = get_prospect_df()
    return df[df["name"].isin(["Anthony Volpe", "Jasson Dominguez", "Ben Rice"])]


def get_org_prospects(org: str) -> pd.DataFrame:
    """Return prospects developed by a specific organization."""
    df = get_prospect_df()
    return df[df["org"] == org]


def get_org_summary() -> pd.DataFrame:
    """Return prospect outcome summary by organization.

    Columns: org, n_prospects, star, solid, disappointing, bust, success_rate
    where success_rate = (star + solid) / total.
    """
    df = get_prospect_df()
    summary = df.groupby("org")["outcome"].value_counts().unstack(fill_value=0)
    for col in ["star", "solid", "disappointing", "bust"]:
        if col not in summary.columns:
            summary[col] = 0
    summary["n_prospects"] = summary.sum(axis=1)
    summary["success_rate"] = (summary["star"] + summary["solid"]) / summary["n_prospects"]
    return summary.reset_index()


# MiLB season-level stats sourced from FanGraphs API (/api/players/stats)
# and Baseball Reference. Includes BB%, K%, wOBA, wRC+ by level/season.
MILB_STATS = {
    "Anthony Volpe": {
        2021: {"level": "A/A+", "pa": 513, "avg": .294, "obp": .423, "slg": .604,
               "bb_pct": .152, "k_pct": .197, "woba": .449, "wrc_plus": 170.8,
               "note": "BA Best Strike-Zone Discipline in Yankees system"},
        2022: {"level": "AA/AAA", "pa": 596, "avg": .249, "obp": .342, "slg": .460,
               "bb_pct": .109, "k_pct": .198, "woba": .352, "wrc_plus": 120.4,
               "note": "65 BB in 132 games; K% held under 20% across levels"},
    },
    "Jasson Dominguez": {
        2022: {"level": "A/A+", "pa": 530, "avg": .273, "obp": .375, "slg": .461,
               "bb_pct": .136, "k_pct": .242, "woba": .383, "wrc_plus": 135.5,
               "note": "508 PA across A and A+"},
        2023: {"level": "AA/AAA", "pa": 544, "avg": .265, "obp": .377, "slg": .425,
               "bb_pct": .153, "k_pct": .244, "woba": .365, "wrc_plus": 125.6,
               "note": "BA Best Strike-Zone Discipline; 15.3% BB rate elite"},
        2024: {"level": "AA/AAA", "pa": 250, "avg": .314, "obp": .376, "slg": .504,
               "bb_pct": .088, "k_pct": .200, "woba": .392, "wrc_plus": 135.7,
               "note": "Rehab + AAA; K% dropped to 20% but BB% cratered"},
    },
    # Comparison prospects (FanGraphs API data)
    "Gunnar Henderson": {
        2021: {"level": "A/A+", "pa": 463, "avg": .258, "obp": .350, "slg": .476,
               "bb_pct": .121, "k_pct": .309, "woba": .364, "wrc_plus": 121.3,
               "note": "High K% but elite power for age-20 season"},
        2022: {"level": "AA/AAA", "pa": 503, "avg": .297, "obp": .416, "slg": .531,
               "bb_pct": .157, "k_pct": .231, "woba": .412, "wrc_plus": 152.0,
               "note": "Massive AA breakout: 15.7% BB rate combined, K% dropped 8 points"},
    },
    "Corbin Carroll": {
        2022: {"level": "AA/AAA", "pa": 442, "avg": .307, "obp": .425, "slg": .610,
               "bb_pct": .152, "k_pct": .242, "woba": .442, "wrc_plus": 144.3,
               "note": "Elite walk rate + power across AA and AAA"},
    },
    "Bobby Witt Jr.": {
        2021: {"level": "AA/AAA", "pa": 564, "avg": .290, "obp": .361, "slg": .575,
               "bb_pct": .090, "k_pct": .232, "woba": .399, "wrc_plus": 140.5,
               "note": "Low BB% but elite bat-to-ball; 23.2% K rate"},
    },
    # Additional Yankees system products for systemic comparison
    "Oswald Peraza": {
        2022: {"level": "AAA", "pa": 480, "avg": .259, "obp": .316, "slg": .399,
               "bb_pct": .081, "k_pct": .209},
    },
    "Ben Rice": {
        2022: {"level": "A", "pa": 290, "avg": .267, "obp": .368, "slg": .442,
               "bb_pct": .131, "k_pct": .210,
               "note": "68 games at Single-A Tampa; solid discipline for first full season"},
        2023: {"level": "A+/AA", "pa": 330, "avg": .324, "obp": .434, "slg": .615,
               "bb_pct": .133, "k_pct": .212,
               "note": "Breakout: 20 HR in 73 games across 3 levels; Yankees MiLB POTY"},
        2024: {"level": "AAA", "pa": 135, "avg": .294, "obp": .428, "slg": .661,
               "bb_pct": .148, "k_pct": .200,
               "note": "Dominated AAA before June call-up; 15% BB rate elite"},
    },
}

# FanGraphs player IDs for API access
FANGRAPHS_IDS = {
    "Anthony Volpe": 27647,
    "Jasson Dominguez": 28080,
    "Ben Rice": 29576,
    "Gunnar Henderson": 26289,
    "Corbin Carroll": 25878,
    "Bobby Witt Jr.": 25764,
}


# Yankees system prospects — derived from main PROSPECT_DATA
YANKEES_SYSTEM = [t for t in PROSPECT_DATA if t[5] == "NYY"]


def get_yankees_system_df() -> pd.DataFrame:
    """Return all Yankees system products for systemic analysis."""
    return pd.DataFrame(
        YANKEES_SYSTEM,
        columns=["name", "mlbam_id", "debut_year", "pre_debut_rank", "outcome", "org"],
    )
