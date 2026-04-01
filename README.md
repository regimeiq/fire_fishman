# fire_fishman 🐟🔥

## A Case Study in Failed Prospect Development

Anthony Volpe and Jasson Dominguez were the Yankees' two highest-profile prospects in a generation. Both had elite physical tools. Both had strong minor league track records. Both are struggling at the MLB level.

This project uses **1.5 million pitches of Statcast data** to diagnose exactly what went wrong, when it went wrong, and how the Yankees' analytics and development pipeline could have prevented it.

## The Central Finding

**The discipline was real — MLB broke it.**

Both prospects had elite plate discipline in the minors. FanGraphs data confirms it: Volpe posted a 15.2% BB rate and sub-20% K rate across A/A+ in 2021 (.449 wOBA, 171 wRC+). Dominguez walked at a 15.3% clip in AA/AAA in 2023 with a 17.3% K rate. These are star-caliber approach numbers by any standard.

Against MLB pitching, both collapsed:

| Metric | Volpe MiLB | Volpe MLB | Dominguez MiLB | Dominguez MLB |
|--------|-----------|-----------|----------------|---------------|
| Chase rate | 15.0% | 30.6% | 17.8% | 31.1% |
| Chase rate (breaking) | 16.7% | 33.0% | 27.3% | 41.3% |
| Chase rate (offspeed) | 29.4% | 39.2% | 20.0% | 39.5% |

The issue isn't talent or discipline — it's **calibration**. Their pitch recognition was trained on minor league stuff. MLB breaking balls break later, tunnel better, and are sequenced by data-driven staffs who already know the weaknesses. The Yankees let their prospects calibrate on the job, in front of 45,000 people, with their confidence on the line.

Compare to Henderson: 30.9% K rate in A-ball → 23.1% in AA with a 19.7% BB rate and .412 wOBA (152 wRC+). He solved pitch recognition *before* his call-up. Volpe's K% plateaued at ~20% across levels — the traditional stats looked great (.423 OBP) while hiding the pitch recognition ceiling underneath.

![MiLB vs MLB](outputs/figures/milb_vs_mlb.png)

## What Separates Stars from Busts?

We tracked 19 recent top-100 prospects and found the three metrics with the largest effect sizes between stars and busts:

| Metric | Stars | Busts | Effect Size |
|--------|-------|-------|-------------|
| Chase rate on offspeed | 38.2% | 42.1% | d = -0.75 |
| Whiff rate vs 96+ mph | 18.6% | 23.8% | d = -0.67 |
| Chase rate on breaking balls | 33.2% | 36.0% | d = -0.64 |

Overall whiff rate (d = -0.08) and zone contact rate (d = -0.02) show almost no separation. **The aggregate metrics hide the signal — you have to look at pitch-type-specific behavior.**

## Different Problems, Same Pipeline Failure

**Volpe** is actually close to star benchmarks on discipline. His biggest issue is **whiff rate against 96+ mph** (22.3% vs 18.6% star avg). He also has a **repeating seasonal collapse** — breaking ball chase rate starts at ~20% each April and spikes to 42-49% by mid-season, in both 2023 and 2024. Henderson (his closest comp) stays flat.

**Dominguez** has a more fundamental recognition problem. **Chase rate on breaking balls: 41.3%** — 8 percentage points above star average and the largest gap in the entire cohort. The league already knows: he sees **18.8% offspeed** vs 13.0% league average. The scouting report is in after just ~400 PA.

![Volpe vs Henderson](outputs/figures/volpe_vs_henderson.png)

## How the Yankees Could Have Prevented This

1. **Statcast-based promotion gates** — Don't promote on slash lines. Gate on the metrics that actually predict translation: whiff rate vs 96+ < 22%, breaking ball chase rate < 35%, offspeed chase rate < 40%. Backtested against the 19-prospect cohort, stars pass 60%+ of gates while disappointing/busts pass < 40%. Traditional stats lie in the minors.

2. **Simulated MLB pitch mixes in development** — Feed prospects the pitch mix they'll actually see. Dominguez sees 18.8% offspeed in the MLB (vs 13.0% league average) — pitchers already know his weakness. He should have been facing that mix in AAA.

3. **Real-time in-season monitoring** — Volpe's breaking ball chase rate going from 20% to 49% in two months is an alarm. A rolling 75-pitch monitoring dashboard with alert thresholds at 40% would have triggered coaching intervention within weeks, not months.

4. **Pre-promotion calibration** — MLB-quality pitch machines, VR pitch recognition training, and AAA coaches instructed to throw MLB-style sequences against top prospects. Henderson's K% dropped 8 points between A-ball and AA — he was being challenged and adapting. Volpe's K% flatlined at ~20% across levels, suggesting he wasn't being pushed.

## It's Not Just Volpe and Dominguez — It's the System

This isn't two isolated cases. The Yankees system has repeatedly produced hitters who win minor league discipline awards and then collapse at the MLB level:

| Player | MiLB Discipline | MLB Result |
|--------|----------------|------------|
| **Volpe** | "Best Strike-Zone Discipline" (BA), .423 OBP | Chase rate doubled, seasonal collapse pattern |
| **Dominguez** | "Best Strike-Zone Discipline" (BA), 17.3% K rate | Chase rate doubled, breaking ball chase 41% |
| **Peraza** | Solid AAA numbers | 35% breaking ball chase, couldn't stick |

The one exception: **Austin Wells** (26.5% chase, 24.6% breaking ball chase). Notably a catcher — he may benefit from seeing pitching from behind the plate.

Meanwhile, the Orioles (Henderson), Diamondbacks (Carroll), Reds (De La Cruz), and Royals (Witt Jr.) consistently translate minor league discipline to the majors. The Yankees have a **development pipeline problem**, not a scouting problem.

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

## Data

All data sourced from public [Statcast](https://baseballsavant.mlb.com) via [pybaseball](https://github.com/jldbc/pybaseball) and [FanGraphs API](https://fangraphs.com).

- **1,503,994 pitches** across 2023-2024 MLB seasons
- **343 pre-debut pitches** (Spring Training / select MiLB Statcast)
- **19 prospect profiles** with complete Statcast data
- **FanGraphs MiLB stats** (BB%, K%, wOBA, wRC+ by level/season) for key prospects via FanGraphs API

## Setup

```bash
git clone https://github.com/regimeiq/fire_fishman.git
cd fire_fishman
pip install -e .

# Pull data (~5 min per season, cached as parquet after first run)
python -c "from fire_fishman.data.statcast import get_statcast_pitches; get_statcast_pitches(2023); get_statcast_pitches(2024)"

jupyter notebook notebooks/
```

## Limitations

- **MiLB sample is small** (89-254 pitches from Spring Training). Directionally strong but not definitive. Full MiLB Statcast is expanding.
- **Prospect cohort is n=19**. Effect sizes are more honest than ML classifiers at this sample size.
- **Temporal aggregation** masks within-season dynamics. Notebook 05 addresses this with monthly breakdowns.

## Tech Stack

Python, pybaseball, pandas, scikit-learn, XGBoost, matplotlib, seaborn
