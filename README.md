# fire_fishman 🐟🔥

## A Case Study in Failed Prospect Development

Anthony Volpe and Jasson Dominguez were the Yankees' two highest-profile prospects in a generation. Both had elite physical tools. Both had strong minor league track records. Both are struggling at the MLB level.

This project uses **1.5 million pitches of Statcast data** to diagnose exactly what went wrong, when it went wrong, and how the Yankees' analytics and development pipeline could have prevented it.

## The Central Finding

**The discipline was real — MLB broke it.**

Both prospects had elite plate discipline in the minors. Volpe's chase rate was 15%. Dominguez's was 18%. These are star-caliber numbers.

Against MLB pitching, both collapsed:

| Metric | Volpe MiLB | Volpe MLB | Dominguez MiLB | Dominguez MLB |
|--------|-----------|-----------|----------------|---------------|
| Chase rate | 15.0% | 30.6% | 17.8% | 31.1% |
| Chase rate (breaking) | 16.7% | 33.0% | 27.3% | 41.3% |
| Chase rate (offspeed) | 29.4% | 39.2% | 20.0% | 39.5% |

The issue isn't talent or discipline — it's **calibration**. Their pitch recognition was trained on minor league stuff. MLB breaking balls break later, tunnel better, and are sequenced by data-driven staffs who already know the weaknesses. The Yankees let their prospects calibrate on the job, in front of 45,000 people, with their confidence on the line.

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

1. **Statcast-based promotion gates** — Don't promote on slash lines. Gate on the metrics that actually predict translation: whiff rate vs 96+ < 22% (6/7 stars pass, 1/3 disappointing pass), breaking ball chase rate < 35% (5/7 stars pass). Traditional stats lie in the minors.

2. **Simulated MLB pitch mixes in development** — Feed prospects the pitch mix they'll actually see. Dominguez should have been facing 18-20% offspeed in AAA, not 13%.

3. **Real-time in-season monitoring** — Volpe's breaking ball chase rate going from 20% to 49% in two months is an alarm. A rolling monitoring dashboard with alert thresholds would have triggered coaching intervention within weeks, not months.

4. **Pre-promotion calibration** — MLB-quality pitch machines, VR pitch recognition training, and AAA coaches instructed to throw MLB-style sequences against top prospects. Bridge the quality gap before the call-up.

## Analysis Modules

| Notebook | Question |
|----------|----------|
| [01 — Translation Gap](notebooks/01_translation_gap.ipynb) | Who has elite tools but poor results? |
| [02 — Pitch Diagnostics](notebooks/02_pitch_diagnostics.ipynb) | Where exactly do Volpe/Dominguez break down? |
| [03 — Effect Sizes](notebooks/03_prediction_model.ipynb) | Which metrics most separate stars from busts? |
| [04 — Prescriptions](notebooks/04_prescriptions.ipynb) | What specific changes would improve their outlook? |
| [05 — Prevention](notebooks/05_prevention_analysis.ipynb) | Monthly trends, pitch mix exploitation, readiness gates |
| [06 — MiLB vs MLB](notebooks/06_milb_vs_mlb.ipynb) | The discipline was real — MLB broke it |

## Data

All data sourced from public [Statcast](https://baseballsavant.mlb.com) via [pybaseball](https://github.com/jldbc/pybaseball) and [FanGraphs](https://fangraphs.com).

- **1,503,994 pitches** across 2023-2024 MLB seasons
- **343 pre-debut pitches** (Spring Training / select MiLB Statcast)
- **19 prospect profiles** with complete Statcast data

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
