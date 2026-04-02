"""Tests for physical tools scoring."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.tools_score import (
    compute_exit_velo_metrics,
    compute_barrel_rate,
    compute_hard_hit_rate,
    compute_tools_score,
    compute_tools_for_cohort,
)


def _make_batted_balls(n=200, batter_id=12345, seed=42):
    """Create synthetic batted ball data."""
    rng = np.random.RandomState(seed)
    return pd.DataFrame({
        "batter": batter_id,
        "launch_speed": rng.uniform(70, 115, size=n),
        "launch_angle": rng.uniform(-20, 60, size=n),
        "barrel": rng.choice([0, 1], size=n, p=[0.92, 0.08]),
    })


class TestComputeExitVeloMetrics:
    def test_returns_expected_keys(self):
        df = _make_batted_balls()
        result = compute_exit_velo_metrics(df, 12345)
        assert "avg_exit_velo" in result
        assert "ev90" in result
        assert "max_exit_velo" in result

    def test_ev90_greater_than_avg(self):
        df = _make_batted_balls(n=500)
        result = compute_exit_velo_metrics(df, 12345)
        assert result["ev90"] >= result["avg_exit_velo"]

    def test_max_greater_than_ev90(self):
        df = _make_batted_balls(n=500)
        result = compute_exit_velo_metrics(df, 12345)
        assert result["max_exit_velo"] >= result["ev90"]

    def test_empty_batter_returns_nans(self):
        df = _make_batted_balls()
        result = compute_exit_velo_metrics(df, 99999)
        assert np.isnan(result["avg_exit_velo"])

    def test_all_nan_launch_speed(self):
        df = pd.DataFrame({
            "batter": [12345] * 5,
            "launch_speed": [np.nan] * 5,
        })
        result = compute_exit_velo_metrics(df, 12345)
        assert np.isnan(result["avg_exit_velo"])


class TestComputeBarrelRate:
    def test_returns_float(self):
        df = _make_batted_balls()
        result = compute_barrel_rate(df, 12345)
        assert isinstance(result, float)

    def test_rate_between_0_and_1(self):
        df = _make_batted_balls(n=500)
        result = compute_barrel_rate(df, 12345)
        assert 0 <= result <= 1

    def test_empty_batter_returns_nan(self):
        df = _make_batted_balls()
        result = compute_barrel_rate(df, 99999)
        assert np.isnan(result)

    def test_uses_native_barrel_column(self):
        df = pd.DataFrame({
            "batter": [12345] * 10,
            "launch_speed": [100.0] * 10,
            "launch_angle": [28.0] * 10,
            "barrel": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        })
        result = compute_barrel_rate(df, 12345)
        assert result == pytest.approx(0.2)

    def test_fallback_without_barrel_column(self):
        df = pd.DataFrame({
            "batter": [12345] * 10,
            "launch_speed": [100.0] * 10,
            "launch_angle": [28.0] * 10,
        })
        result = compute_barrel_rate(df, 12345)
        # All meet barrel criteria: EV=100, LA=28 is within range
        assert result == 1.0


class TestComputeHardHitRate:
    def test_rate_between_0_and_1(self):
        df = _make_batted_balls(n=500)
        result = compute_hard_hit_rate(df, 12345)
        assert 0 <= result <= 1

    def test_all_hard_hit(self):
        df = pd.DataFrame({
            "batter": [12345] * 5,
            "launch_speed": [100.0] * 5,
        })
        assert compute_hard_hit_rate(df, 12345) == 1.0

    def test_none_hard_hit(self):
        df = pd.DataFrame({
            "batter": [12345] * 5,
            "launch_speed": [80.0] * 5,
        })
        assert compute_hard_hit_rate(df, 12345) == 0.0


class TestComputeToolsScore:
    def test_returns_all_metrics(self):
        df = _make_batted_balls()
        result = compute_tools_score(df, 12345)
        assert "avg_exit_velo" in result
        assert "barrel_rate" in result
        assert "hard_hit_rate" in result


class TestComputeToolsForCohort:
    def test_returns_dataframe_with_z_scores(self):
        rng = np.random.RandomState(42)
        ids = [100, 200, 300]
        rows = []
        for bid in ids:
            for _ in range(50):
                rows.append({
                    "batter": bid,
                    "launch_speed": rng.uniform(80, 110),
                    "launch_angle": rng.uniform(-10, 50),
                    "barrel": rng.choice([0, 1], p=[0.9, 0.1]),
                })
        df = pd.DataFrame(rows)
        result = compute_tools_for_cohort(df, ids)
        assert "tools_composite_z" in result.columns
        assert len(result) == 3

    def test_z_scores_centered(self):
        rng = np.random.RandomState(42)
        ids = [100, 200, 300, 400, 500]
        rows = []
        for bid in ids:
            for _ in range(100):
                rows.append({
                    "batter": bid,
                    "launch_speed": rng.uniform(80, 110),
                    "launch_angle": rng.uniform(-10, 50),
                    "barrel": rng.choice([0, 1], p=[0.9, 0.1]),
                })
        df = pd.DataFrame(rows)
        result = compute_tools_for_cohort(df, ids)
        # Z-scores should be approximately centered at 0
        assert abs(result["avg_exit_velo_z"].mean()) < 0.01

    def test_identical_batters_zero_std(self):
        """When all batters have identical stats, z-scores should be 0."""
        ids = [100, 200]
        rows = []
        for bid in ids:
            for _ in range(50):
                rows.append({
                    "batter": bid,
                    "launch_speed": 95.0,
                    "launch_angle": 25.0,
                    "barrel": 0,
                })
        df = pd.DataFrame(rows)
        result = compute_tools_for_cohort(df, ids)
        # Should not raise and z-scores should be 0
        assert result["tools_composite_z"].iloc[0] == 0.0
