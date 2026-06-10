# Yankees Analytics Audit

## Baseball Analytics Case Study

This repository is a public-data case study of Yankees roster construction and player development from 2017-2026. It uses Statcast, FanGraphs, and curated prospect data to examine where measurable strengths translated into MLB performance and where they did not.

The project is intentionally framed as an analytical audit: it evaluates decisions, outcomes, and uncertainty using reproducible code and public data. It is not a claim of causality, and it does not require agreement with every baseball interpretation to inspect the workflow.

Portfolio page: https://wksprojects.com/baseball-analytics-case-study/

## Question Studied

How well did Yankees player development and roster construction translate measurable inputs into MLB value?

The analysis focuses on five related questions:

| Area | Question |
| --- | --- |
| Prospect development | Did elite minor league plate discipline translate against MLB pitch quality? |
| Pitch recognition | Which pitch-level metrics separate successful prospects from disappointing outcomes? |
| Roster construction | Did the roster over-index on extreme player profiles rather than balanced contributors? |
| Baserunning and defense | How much value did the team gain or lose in non-hitting components? |
| Team value composite | Can pressure performance, baserunning, and defense explain team WAR beyond offense? |

## Data Sources

All data comes from public sources through Python tooling:

| Dataset | Coverage | Use |
| --- | --- | --- |
| Statcast pitch-level data | 2021-2026 | Plate discipline, whiff rates, exit velocity, launch angle, batted-ball direction |
| FanGraphs team batting | 2017-2024 | BsR, UBR, wSB, HR dependency, offensive context |
| FanGraphs team fielding | 2017-2024 | OAA, DRS, UZR, Def |
| FanGraphs player batting | 2021-2025 | Barrel%, K%, BB%, wOBA, wRC+, roster archetypes |
| Curated prospect cohort | 43 prospects, 21 organizations | Translation gaps, readiness gates, org-level comparison |
| MiLB development records | Selected prospect careers | Pre-/post-debut plate discipline context |

## Methods

- Vectorized pandas feature engineering for pitch-level plate discipline, pitch-type whiff rates, velocity tiers, batted-ball quality, and tools-to-production translation gaps.
- Z-scored tools and team components within comparison groups to control for scale differences.
- Effect size analysis for small prospect cohorts, with machine-learning models used only as sanity checks.
- Linear regression, 10-fold cross-validation, and Bayesian regression for the team-level value composite.
- Explicit limitations for sample size, observational inference, and same-year versus year-ahead validation.

Additional detail: [docs/methodology.md](docs/methodology.md) and [docs/limitations.md](docs/limitations.md).

## Key Findings

| Finding | Evidence | Interpretation |
| --- | --- | --- |
| Prospect translation issues were velocity- and pitch-specific. | Whiff rate against 96+ mph velocity separated stronger outcomes from weaker ones most clearly in the cohort, with pitch-type whiff rates next; cohort-level chase-rate differences were small, and the chase-rate collapse appears specifically in the Yankees case studies. | Aggregate discipline metrics can hide the exact failure mode. |
| Ben Rice was the strongest internal counterexample. | Rice held a lower chase-rate profile and passed 5/5 readiness gates; Volpe and Dominguez each passed 4/5, while Peraza passed 3/5. Rice then broke out in 2025 and had a strong early-2026 public-data sample. | The framework did not simply label all Yankees prospects as failures; it identified a different readiness profile. |
| Dominguez and Volpe remain live evaluations. | Dominguez's May 2026 shoulder injury interrupts the signal; Volpe's swing-plane adjustment should be monitored before updating the read. | These cases should be treated as ongoing, not closed. |
| Org-level development outcomes differed materially. | The curated cohort shows Baltimore at 100% successful outcomes (5/5), Cleveland at 60% (3/5), and the Yankees at 33% (2/6) among target organizations. | The sample is modest, but the pattern supports further investigation into development process differences. |
| Baserunning value declined from a prior strength. | Yankees BsR moved from +7.6 in 2017 to -17.2 in 2024, with a cumulative -39.2 BsR from 2018-2024. | The loss was broader than stolen bases; UBR and extra-base advancement were part of the decline. |
| Defensive value was available but inconsistently prioritized. | The team was near the bottom of OAA from 2018-2021, then improved sharply in 2022. | Defensive underperformance appears to have been a roster-construction choice rather than a fixed constraint. |
| Balanced roster profiles mattered. | Contenders tended to carry more complete hitters, while several Yankees rosters leaned toward all-or-nothing power or low-impact contact profiles. | Roster balance is a measurable construction issue, not only a stylistic preference. |
| The team-level value composite added signal beyond offense. | The pressure/baserunning/defense composite correlated with WAR (same-year r = +0.34; year-ahead r = +0.24) and was tested with linear and Bayesian regression. | The metric is exploratory and should be interpreted as a compact summary of non-offensive value, not a causal model. |

## 2026 Live Update

As of the project snapshot in early June 2026, Ben Rice is the strongest live validation case in the project: his 2025 breakout and strong early-2026 offensive sample align with the readiness-gate profile identified in Notebook 10. Because the 2026 season is ongoing, the final read should be revisited after the year.

Dominguez is temporarily paused as an evaluation case after a May 2026 shoulder injury. Volpe remains a monitoring case because any swing-plane adjustment needs a larger sample before changing the underlying conclusion.

## Notebooks

| Notebook | Focus |
| --- | --- |
| [01 - Translation Gap](notebooks/01_translation_gap.ipynb) | Tools versus MLB production |
| [02 - Pitch Diagnostics](notebooks/02_pitch_diagnostics.ipynb) | Pitch-type and count-specific vulnerabilities |
| [03 - Effect Sizes](notebooks/03_prediction_model.ipynb) | Metrics that separate stronger and weaker outcomes |
| [04 - Prescriptions](notebooks/04_prescriptions.ipynb) | Player-specific development priorities |
| [05 - Prevention](notebooks/05_prevention_analysis.ipynb) | Monthly trends, pitch mix, readiness gates |
| [06 - MiLB vs MLB](notebooks/06_milb_vs_mlb.ipynb) | Minor league discipline versus MLB translation |
| [07 - Systemic Analysis](notebooks/07_yankees_systemic.ipynb) | Organization-level prospect outcomes |
| [08 - Yankees Case Studies](notebooks/08_yankees_case_studies.ipynb) | Baserunning, defense, HR dependency, roster extremes |
| [09 - Team Value Composite](notebooks/09_team_value_composite.ipynb) | Pressure, baserunning, defense, and WAR |
| [10 - Ben Rice Comparison](notebooks/10_rice_comparison.ipynb) | Rice versus Volpe, Dominguez, and Peraza |
| [11 - Roster Balance](notebooks/11_role_player_profile.ipynb) | Hitter archetypes and roster depth |
| [12 - Lineup Fit Exploration](notebooks/12_ideal_lineup.ipynb) | Experimental role-fit scoring |

## Reproducibility

```bash
git clone https://github.com/regimeiq/fire_fishman.git
cd fire_fishman
pip install -e .

python -c "
from fire_fishman.data.statcast import get_statcast_pitches, get_batting_stats
for year in range(2021, 2027):
    get_statcast_pitches(year)
    get_batting_stats(year)
"

pytest -q
```

The data fetch is cached as parquet after the first run. Some notebooks rely on external APIs and may take several minutes to execute on a fresh machine.

## Limitations

This is an observational analysis using public data. It can identify measurable patterns and missed value, but it cannot fully observe coaching decisions, player health, private tracking data, or internal model outputs. The prospect cohort is modest, some MiLB samples are small, and the team-level composite is primarily descriptive.

See [docs/limitations.md](docs/limitations.md) for the full limitations register.

## Repository Guide

| Path | Purpose |
| --- | --- |
| `src/fire_fishman/` | Reusable feature engineering and data helpers |
| `notebooks/` | Case-study analyses |
| `outputs/figures/` | Generated visual outputs |
| `outputs/summary.md` | Concise findings table |
| `docs/methodology.md` | Methodology details |
| `docs/limitations.md` | Limitations and interpretation guidance |
