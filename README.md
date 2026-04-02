# fire_fishman

## Quantifying Systemic Failures in Yankees Analytics (2017-2024)
**Prospect Development, Roster Construction, and an Original Composite Metric for Intangible Contributions**

Michael Fishman has run the Yankees' analytics department since 2005. Under his leadership, the Yankees have made a series of analytically-driven decisions that were demonstrably wrong — not just in hindsight, but provably wrong with data that was available at the time.

This project uses **3M+ pitches of Statcast data (2021-2026)**, **FanGraphs team and player statistics (2017-2025)**, **MiLB development records**, and **regression analysis with cross-validation** to quantify the damage across seven analyses:

1. **Prospect Development** — Elite minor league hitters systematically collapsed at the MLB level because the pipeline didn't prepare them for MLB pitch recognition
2. **Baserunning Philosophy** — Abandoned stolen bases and baserunning fundamentals, going from 7th in BsR to dead last while becoming the most HR-dependent team in baseball
3. **Defensive Neglect** — 2nd worst OAA in baseball (2018-2021), costing 7.0 wins, then jumped to #1 DRS in 2022 proving the talent was always available
4. **The Dawg Metric** — An original composite metric (pressure + hustle + grit) that predicts team WAR (r = +0.30) independently of offensive talent, validated via 10-fold CV and linear + Bayesian regression
5. **The Extremes Trap** — Oscillating between all-or-nothing sluggers (Gallo: 18.5% barrel rate, 37.7% K) and contactless slap hitters (IKF: 1.0% barrel rate, .650 OPS) while contenders built complete hitters
6. **The Diamond in the Rough** — A 12th-round pick holds his discipline (21% chase rate) while the "next Mickey Mantle" and a 1st-rounder both collapse at 31% — why did the org's least-hyped prospect succeed where the blue chips failed?
7. **Roster Construction** — Profiling the archetypes contenders actually build (complete hitters, speed/defense specialists, platoon bats, table-setters) vs the Yankees' extreme-only approach

---

## Key Findings

### 1. The Prospect Pipeline ([Notebooks 01-07, 10](notebooks/))

Volpe and Dominguez had elite minor league discipline — both won BA's "Best Strike-Zone Discipline" — then collapsed at the MLB level. Chase rates doubled for both. Meanwhile, Rice (12th-round pick, 14.8% MiLB BB rate) held his chase rate at 23% and broke out in 2025. The pattern suggests a systemic development issue, not individual talent failures. Across a prospect cohort, the metrics that separate stars from busts are pitch-type-specific (offspeed chase, fastball whiff) — not aggregate whiff or zone contact.

### 2. Baserunning: 7th to Dead Last ([Notebook 08](notebooks/08_fishman_case_studies.ipynb))

BsR collapsed from +7.6 (7th, 2017) to -17.2 (30th, 2024). Total: -39.2 BsR = 3.9 wins lost. The UBR collapse (extra base taking: +9.7 → -10.9) is worse than the stolen base issue — this is a team that can't run the bases under any circumstances.

### 3. Defensive Neglect: 7.0 Wins Lost ([Notebook 08](notebooks/08_fishman_case_studies.ipynb))

2nd worst OAA in baseball (2018-2021), -70.4 Def runs = 7.0 wins lost. Then 2022: jumped to #1 DRS. The talent was always available — they just chose not to prioritize it. The 2022 team proves you can fix defense overnight, but they never fixed baserunning (Hustle = -0.98, worst among top-10 Dawg teams).

### 4. The Dawg Metric ([Notebook 09](notebooks/09_dawg_metric.ipynb))

An original composite (Pressure + Hustle + Grit, z-scored within season) that correlates with WAR (r = +0.30, year-ahead r = +0.22) independently of offensive talent (r = +0.09 vs wRC+). Validated via linear regression with 10-fold CV and Bayesian regression (Dawg coefficient: +4.0 WAR per 1 SD, 94% HDI [+2.7, +5.3], P(dawg > 0) = 1.0). The Yankees ranked bottom-third for most of 2017-2024.

### 5. The Extremes Trap ([Notebooks 08, 11](notebooks/))

Gallo (37.7% K, 84 wRC+) and IKF (1.0% barrel, 84 wRC+) — opposite extremes, same result. Contenders carried 3-4 "complete hitters" (K% < 25%, Barrel% > 6%, BB% > 8%). The Yankees typically had 1-2 (reaching 3 only in 2024 with Soto). The roster construction philosophy acquired extremes instead of building balance.

### 6. The Diamond in the Rough ([Notebook 10](notebooks/10_rice_comparison.ipynb))

Rice (chase 23.4%, barrel 15.4%) vs Volpe (chase 29.5%, barrel 10.5%) vs Dominguez (chase 33.1%, barrel 7.0%). Same org, same park — wildly different outcomes. Rice passes 5/5 readiness gates; Dominguez passes 2/5. The prospects they invested the most in collapsed; the lower-profile guy figured it out.

### 7. Roster Construction ([Notebook 11](notebooks/11_role_player_profile.ipynb))

Contenders carry distinct archetypes (stars, complete hitters, speed/defense specialists, platoon bats, table-setters). The Yankees filled 3+ spots with the same extreme. The 2022 Astros carried 4 complete hitters; the 2024 Dodgers had 3 (Ohtani, Freeman, W. Smith). The Yankees typically had 1-2 before the Soto acquisition.

---

## The Fishman Scorecard

| Bad Take | Damage | Period |
|----------|--------|--------|
| Prospect pipeline doesn't prepare for MLB pitch recognition | Stars pass 60%+ of Statcast gates; Yankees busts pass <40% | 2019-2024 |
| Abandoned baserunning as competitive tool | -39.2 BsR = 3.9 wins lost; 30th by 2024 | 2018-2024 |
| Neglected defense for 4 years | -70.4 Def runs = 7.0 wins lost; -105 OAA | 2018-2021 |
| #1 most HR-dependent team with no Plan B | 3 years at #1; can't win in October | 2018-2023 |
| Zero investment in "Dawg" (clutch + hustle + grit) | Dawg correlates with WAR (r=+0.30, year-ahead r=+0.22) independent of talent; Yankees bottom-third | 2017-2024 |
| Acquired extremes instead of complete hitters (Gallo/IKF) | 1-2 "sweet spot" batters vs 3-4 for contenders; same blind spot as prospect pipeline | 2021-2023 |

**Documented damage: ~10.9 wins** — 3.9 from baserunning (BsR, 2018-2024) and 7.0 from defense (Def, 2018-2021). These are independent FanGraphs metrics with no overlap. Note the time periods differ: BsR spans 7 seasons while Def spans the 4-year neglect window before the 2022 correction.

That doesn't include the prospect development failures, the October collapses, or the opportunity cost of building a one-dimensional roster.

The fix was always available — the 2022 team proved it, and Ben Rice proved it again in 2025. The talent was never the problem.

---

## Analysis Modules

| Notebook | Question |
|----------|----------|
| [01 — Translation Gap](notebooks/01_translation_gap.ipynb) | Who has elite tools but poor results? |
| [02 — Pitch Diagnostics](notebooks/02_pitch_diagnostics.ipynb) | Where exactly do Volpe/Dominguez break down? |
| [03 — Effect Sizes](notebooks/03_prediction_model.ipynb) | Which metrics most separate stars from busts? |
| [04 — Prescriptions](notebooks/04_prescriptions.ipynb) | What specific changes would improve their outlook? |
| [05 — Prevention](notebooks/05_prevention_analysis.ipynb) | Monthly trends, pitch mix exploitation, readiness gates |
| [06 — MiLB vs MLB](notebooks/06_milb_vs_mlb.ipynb) | The discipline was real — MLB broke it |
| [07 — Systemic Analysis](notebooks/07_yankees_systemic.ipynb) | Why this keeps happening to the Yankees |
| [08 — Fishman's Bad Takes](notebooks/08_fishman_case_studies.ipynb) | Baserunning, defense, HR dependency, 2022 paradox, extremes trap |
| [09 — Dawg Metric Deep Dive](notebooks/09_dawg_metric.ipynb) | Independence test, regression, year-ahead prediction, playoff model |
| [10 — Rice: The Counter-Example](notebooks/10_rice_comparison.ipynb) | Ben Rice vs Volpe/Dominguez/Peraza — what success looks like |
| [11 — Roster Balance Analysis](notebooks/11_role_player_profile.ipynb) | How contenders build roster depth vs the Yankees' extreme-only approach |

## Data

All data sourced from public [Statcast](https://baseballsavant.mlb.com) via [pybaseball](https://github.com/jldbc/pybaseball) and [FanGraphs API](https://fangraphs.com).

| Dataset | Volume | Coverage | Use |
|---------|--------|----------|-----|
| Statcast pitch-level | **3M+ pitches** | 2021-2026 | Plate discipline, whiff rates, exit velo, batted ball direction |
| FanGraphs team batting | **240 team-seasons** | 2017-2024 | BsR, UBR, wSB, lineup handedness, HR dependency |
| FanGraphs team fielding | **240 team-seasons** | 2017-2024 | OAA, DRS, UZR, Def |
| FanGraphs player batting | **2,500+ player-seasons** | 2021-2025 | Barrel%, K%, BB%, wOBA, wRC+, hitter archetype classification |
| Dawg metric regression | **216 team-seasons** | 2017-2024 | Linear regression, 10-fold CV, playoff prediction |
| Prospect profiles | **24 prospects** | 2019-2026 debuts | Tools scores, translation gaps, readiness gates |
| MiLB stats | **10 prospect careers** | 2021-2024 | BB%, K%, wOBA, wRC+ by level for pre-/post-debut comparison |
| Pre-debut Statcast | **343 pitches** | Spring Training / MiLB | Pitch recognition calibration baseline |

## Setup

```bash
git clone https://github.com/regimeiq/fire_fishman.git
cd fire_fishman
pip install -e .

# Pull data (~5 min per season, cached as parquet after first run)
python -c "
from fire_fishman.data.statcast import get_statcast_pitches, get_batting_stats
for year in range(2021, 2027):
    get_statcast_pitches(year)
    get_batting_stats(year)
"

jupyter notebook notebooks/
```

## Methods

| Method | Application | Why |
|--------|-------------|-----|
| **Linear + Bayesian regression** (sklearn, Bambi/PyMC) | Dawg metric → WAR relationship | Frequentist with 10-fold CV; Bayesian via Bambi for posterior credible intervals and WAIC model comparison |
| **Effect size analysis** (Cohen's d) | Star vs bust separation on small prospect cohort | More honest than ML classifiers at small n |
| **10-fold cross-validation** | Dawg playoff prediction model | Standard validation; KFold with shuffle for team-season data |
| **Z-scoring within season** | All Dawg components, tools scores | Controls for year-over-year league-wide shifts |
| **XGBoost** (sanity check) | Feature importance for prospect translation | LOO-CV, used to confirm effect size rankings |
| **Statcast-based readiness gates** | Prospect call-up framework | Pitch-type-specific thresholds derived from star 75th percentiles |
| **Hitter archetype classification** | Roster construction analysis | Multi-dimensional profiling (barrel%, K%, BB%, BsR) |

## Limitations

- **MiLB sample is small** (89-254 pitches from Spring Training). Directionally strong but not definitive.
- **Prospect cohort is small (n~20)**. Effect sizes are more honest than ML classifiers at this sample size, but findings are suggestive and hypothesis-generating, not proof of causation.
- **Baserunning estimates are conservative** — BsR captures runs above average, not the full opportunity cost of the philosophy.
- **Rice's 2024 MLB sample is small** (~180 PA, 50 games). The 2025 full season (530 PA) is the meaningful data point.
- **Dawg metric validation is primarily same-year.** The r = +0.30 and R² improvement are in-sample (with 10-fold CV). The year-ahead correlation (r = +0.22) is the true out-of-sample test. The playoff prediction proxy (top-12 WAR teams) is defined from the same data used to build the metric.

## Tech Stack

| | |
|---|---|
| **Core** | Python 3.11+, pandas 2.0+, NumPy |
| **Data** | pybaseball (Statcast + FanGraphs API), parquet caching |
| **Statistical modeling** | scikit-learn, XGBoost, PyMC, Bambi, ArviZ |
| **Visualization** | matplotlib, seaborn |
| **Infrastructure** | Jupyter notebooks, pip-installable package (`src/fire_fishman/`), git |
