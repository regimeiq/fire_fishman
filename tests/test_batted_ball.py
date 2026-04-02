"""Tests for batted ball direction classification and park factor analysis."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.batted_ball import (
    PULL_THRESHOLD_RF,
    PULL_THRESHOLD_LF,
    SHORT_PORCH_MAX_DISTANCE,
    classify_hit_direction,
    classify_hit_directions,
    is_short_porch_hr,
    compute_yankee_stadium_hr_splits,
    compute_park_hr_factor_by_hand,
)


class TestClassifyHitDirection:
    def test_lhh_pull_to_right_field(self):
        assert classify_hit_direction(170, "L") == "pull"

    def test_lhh_oppo_to_left_field(self):
        assert classify_hit_direction(80, "L") == "oppo"

    def test_lhh_center(self):
        assert classify_hit_direction(125, "L") == "center"

    def test_rhh_pull_to_left_field(self):
        assert classify_hit_direction(80, "R") == "pull"

    def test_rhh_oppo_to_right_field(self):
        assert classify_hit_direction(170, "R") == "oppo"

    def test_rhh_center(self):
        assert classify_hit_direction(125, "R") == "center"

    def test_switch_hitter_treated_as_rhh(self):
        assert classify_hit_direction(80, "S") == "pull"

    def test_nan_returns_nan(self):
        result = classify_hit_direction(np.nan, "L")
        assert pd.isna(result)

    def test_boundary_values(self):
        # On the threshold = center (not pull/oppo)
        assert classify_hit_direction(PULL_THRESHOLD_RF, "L") == "center"
        assert classify_hit_direction(PULL_THRESHOLD_LF, "L") == "center"


class TestClassifyHitDirections:
    def test_vectorized_matches_scalar(self):
        df = pd.DataFrame({
            "hc_x": [170, 80, 125, 80, 170, np.nan],
            "stand": ["L", "L", "L", "R", "R", "L"],
        })
        result = classify_hit_directions(df)
        expected = ["pull", "oppo", "center", "pull", "oppo", np.nan]
        for actual, exp in zip(result, expected):
            if pd.isna(exp):
                assert pd.isna(actual)
            else:
                assert actual == exp


class TestIsShortPorchHr:
    def test_identifies_short_porch_hr(self):
        df = pd.DataFrame({
            "home_team": ["NYY"],
            "events": ["home_run"],
            "hc_x": [170.0],
            "hit_distance_sc": [330.0],
        })
        assert is_short_porch_hr(df).iloc[0] == True

    def test_rejects_non_yankee_stadium(self):
        df = pd.DataFrame({
            "home_team": ["BOS"],
            "events": ["home_run"],
            "hc_x": [170.0],
            "hit_distance_sc": [330.0],
        })
        assert is_short_porch_hr(df).iloc[0] == False

    def test_rejects_long_hr(self):
        df = pd.DataFrame({
            "home_team": ["NYY"],
            "events": ["home_run"],
            "hc_x": [170.0],
            "hit_distance_sc": [400.0],
        })
        assert is_short_porch_hr(df).iloc[0] == False

    def test_rejects_non_hr(self):
        df = pd.DataFrame({
            "home_team": ["NYY"],
            "events": ["single"],
            "hc_x": [170.0],
            "hit_distance_sc": [330.0],
        })
        assert is_short_porch_hr(df).iloc[0] == False


class TestComputeYankeeStadiumHrSplits:
    def test_returns_expected_columns(self):
        df = pd.DataFrame({
            "home_team": ["NYY"] * 10,
            "events": ["home_run"] * 10,
            "hc_x": [170, 170, 80, 80, 125, 170, 80, 125, 170, 80],
            "stand": ["L", "L", "L", "R", "R", "R", "R", "L", "L", "R"],
            "launch_speed": [105] * 10,
            "hit_distance_sc": [400] * 10,
        })
        result = compute_yankee_stadium_hr_splits(df)
        assert "stand" in result.columns
        assert "direction" in result.columns
        assert "hr_count" in result.columns
        assert "pct_of_total" in result.columns
        assert abs(result["pct_of_total"].sum() - 1.0) < 0.01


class TestComputeParkHrFactorByHand:
    def test_neutral_park(self):
        rng = np.random.RandomState(42)
        n = 2000
        teams = rng.choice(["NYY", "BOS", "LAD", "HOU", "CHC"], size=n)
        events = rng.choice(["home_run", "single", "double", "field_out"], size=n,
                            p=[0.03, 0.15, 0.05, 0.77])
        df = pd.DataFrame({
            "home_team": teams,
            "events": events,
            "stand": rng.choice(["L", "R"], size=n),
        })
        result = compute_park_hr_factor_by_hand(df, "NYY")
        # With uniform random data, park factor should be near 1.0
        assert 0.3 < result["LHH_park_factor"] < 3.0
        assert 0.3 < result["RHH_park_factor"] < 3.0

    def test_excludes_target_park_from_baseline(self):
        # All HRs at NYY, none elsewhere — factor should be > 1.0
        df = pd.DataFrame({
            "home_team": ["NYY", "NYY", "NYY", "BOS", "BOS", "BOS"],
            "events": ["home_run", "home_run", "field_out", "field_out", "field_out", "field_out"],
            "stand": ["L", "L", "L", "L", "L", "L"],
        })
        result = compute_park_hr_factor_by_hand(df, "NYY")
        # NYY: 2/3 HR rate, BOS: 0/3 HR rate — league (excl NYY) has 0 HRs
        # league_hr_rate = 0, so factor defaults to 1.0
        assert result["LHH_park_factor"] == 1.0
