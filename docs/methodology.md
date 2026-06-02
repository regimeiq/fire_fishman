# Methodology

## Overview

This project evaluates Yankees player development and roster construction using public Statcast and FanGraphs data. The workflow is organized around reproducible feature engineering, small-cohort statistical comparisons, and explicitly labeled exploratory models.

## Data Collection

| Source | Coverage | Notes |
| --- | --- | --- |
| Statcast via `pybaseball` | 2021-2026 pitch-level data | Cached locally as parquet after first fetch. |
| FanGraphs team batting and fielding | 2017-2024 | Used for baserunning, fielding, offensive context, and team-level value metrics. |
| FanGraphs player batting | 2021-2025 | Used for hitter archetype and roster-balance analysis. |
| Curated prospect list | 43 prospects across 16 organizations | Includes MLBAM ids, debut year, pre-debut rank, organization, and broad outcome bucket. |
| MiLB public records | Selected player-seasons | Used for pre-debut discipline context. |

## Feature Engineering

Pitch-level features are computed with vectorized pandas operations:

- In-zone and out-of-zone classification from plate location and batter strike-zone bounds.
- Swing, whiff, chase, and zone-contact rates from Statcast pitch descriptions.
- Pitch group mapping into fastball, breaking, offspeed, and other.
- Count-state splits for hitter-ahead, pitcher-ahead, even, and two-strike counts.
- Velocity-tier splits for sub-90, 90-93, 93-96, and 96+ mph pitches.
- Batted-ball quality metrics including exit velocity, 90th percentile exit velocity, hard-hit rate, and barrel rate.

The tools-to-production translation analysis combines physical tools metrics with MLB production indicators such as wOBA and wRC+.

## Prospect Analysis

The prospect analysis is intentionally conservative because the cohort is small. It uses:

- Cohort-level comparisons across player outcomes.
- Pitch-type-specific feature differences rather than aggregate-only metrics.
- Effect sizes to describe separation between outcome groups.
- Readiness gates derived from successful-prospect benchmarks.
- Organization-level summaries treated as hypothesis-generating rather than definitive.

## Team-Level Analysis

The team-level analysis uses FanGraphs data to study baserunning, defense, offensive dependence, and roster shape. The pressure/baserunning/defense composite is built from z-scored components within season so that league environment shifts do not dominate the comparison.

The composite is tested with:

- Same-year correlation against team WAR.
- Year-ahead correlation as a more demanding out-of-sample check.
- Linear regression with cross-validation.
- Bayesian regression for uncertainty intervals.

The composite should be read as a compact descriptive metric for non-offensive value. It is not a causal model.

## Reproducibility

Core package behavior is covered by unit tests. The notebooks are stored with outputs cleared to avoid local path leakage and stale execution artifacts. Figures are retained in `outputs/figures/` as generated artifacts.
