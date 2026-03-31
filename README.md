# fire_fishman 🐟🔥

## Why Do Elite MLB Prospects Fail?

Top prospects like Anthony Volpe and Jasson Dominguez arrive with elite physical tools — bat speed, exit velocity, barrel rate — yet struggle at the MLB level. The scouting grades are there. The Statcast numbers say the raw ability is real. So why don't the results follow?

This project models the **tools-to-production translation gap**: the disconnect between what a prospect *can* do physically and what they *actually* produce. We use pitch-level Statcast data to diagnose *where* elite prospects break down against MLB pitching and build a predictive model to identify which early-career signals separate future stars from busts.

## Key Questions

1. **Who has the biggest translation gap?** Among recent top-100 prospects, who has elite tools but poor results — and vice versa?
2. **Where do they break?** Is it chase rate? Breaking ball whiffs? Velocity vulnerability? Count-specific collapse?
3. **Can we predict it?** Using pitch-level data from a prospect's first ~200 PA, can we predict whether they'll figure it out?
4. **What's the prescription?** For each underperformer, what specific development changes would the model recommend?

## Analysis Modules

| Notebook | Question | Method |
|----------|----------|--------|
| [01 — Translation Gap](notebooks/01_translation_gap.ipynb) | Who converts tools into production? | Statcast tools score vs. wOBA, scatter analysis |
| [02 — Pitch Diagnostics](notebooks/02_pitch_diagnostics.ipynb) | Where do Volpe/Dominguez break? | Chase rate, whiff splits by pitch type/velo/count |
| [03 — Prediction Model](notebooks/03_prediction_model.ipynb) | Which metrics predict success? | XGBoost feature importance + Bayesian logistic regression |
| [04 — Prescriptions](notebooks/04_prescriptions.ipynb) | What should they work on? | Sensitivity analysis, comparable prospect matching |

## Selected Findings

*Run the notebooks to populate — key figures are saved to `outputs/figures/`.*

## Data

All data sourced from public Statcast (via [pybaseball](https://github.com/jldbc/pybaseball)) and FanGraphs. No proprietary data used.

- Pitch-level Statcast data (2023-2024): ~1.4M pitches
- Season-level batting stats from FanGraphs
- Prospect cohort: ~25 recent top-100 prospects who debuted 2019-2024

## Setup

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/fire_fishman.git
cd fire_fishman
uv sync  # or: pip install -e .

# Pull data (takes ~5 min per season on first run, then cached)
python -c "from fire_fishman.data.statcast import get_statcast_pitches; get_statcast_pitches(2023); get_statcast_pitches(2024)"

# Run notebooks
jupyter notebook notebooks/
```

## Tech Stack

- **pybaseball** — Statcast + FanGraphs data access
- **pandas** — data wrangling
- **XGBoost + scikit-learn** — feature importance
- **PyMC + Bambi** — Bayesian modeling with honest uncertainty
- **ArviZ** — posterior diagnostics
- **matplotlib + seaborn** — visualization

## Project Structure

```
fire_fishman/
├── src/fire_fishman/
│   ├── data/          # Statcast fetching, prospect lists, caching
│   └── features/      # Tools score, pitch-level metrics, translation gap
├── notebooks/         # Analysis modules (01-04)
├── outputs/figures/   # Publication-quality plots
└── pyproject.toml
```

## Why This Matters

Every front office is trying to answer this question. The difference between a prospect who converts and one who doesn't is worth tens of millions of dollars in roster decisions, trade value, and development investment. Physical tools are necessary but not sufficient — the translation gap is where the alpha is.
