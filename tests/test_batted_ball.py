"""Tests for batted ball direction classification."""

import numpy as np
import pandas as pd

from fire_fishman.features.batted_ball import (
    PULL_THRESHOLD_RF,
    PULL_THRESHOLD_LF,
    classify_hit_directions,
    is_short_porch_hr,
    compute_yankee_stadium_hr_splits,
)


class TestClassifyHitDirections:
    def _classify(self, hc_x, stand):
        return classify_hit_directions(pd.DataFrame({"hc_x": [hc_x], "stand": [stand]})).iloc[0]

    def test_lhh_directions(self):
        assert self._classify(170, "L") == "pull"
        assert self._classify(80, "L") == "oppo"
        assert self._classify(125, "L") == "center"

    def test_rhh_directions(self):
        assert self._classify(80, "R") == "pull"
        assert self._classify(170, "R") == "oppo"
        assert self._classify(125, "R") == "center"

    def test_switch_hitter_treated_as_rhh(self):
        assert self._classify(80, "S") == "pull"

    def test_nan_returns_nan(self):
        assert pd.isna(self._classify(np.nan, "L"))

    def test_boundary_values(self):
        # On the threshold = center (not pull/oppo)
        assert self._classify(PULL_THRESHOLD_RF, "L") == "center"
        assert self._classify(PULL_THRESHOLD_LF, "L") == "center"

    def test_vectorized_over_mixed_frame(self):
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
        assert is_short_porch_hr(df).iloc[0]

    def test_rejects_non_yankee_stadium(self):
        df = pd.DataFrame({
            "home_team": ["BOS"],
            "events": ["home_run"],
            "hc_x": [170.0],
            "hit_distance_sc": [330.0],
        })
        assert not is_short_porch_hr(df).iloc[0]

    def test_rejects_long_hr(self):
        df = pd.DataFrame({
            "home_team": ["NYY"],
            "events": ["home_run"],
            "hc_x": [170.0],
            "hit_distance_sc": [400.0],
        })
        assert not is_short_porch_hr(df).iloc[0]

    def test_rejects_non_hr(self):
        df = pd.DataFrame({
            "home_team": ["NYY"],
            "events": ["single"],
            "hc_x": [170.0],
            "hit_distance_sc": [330.0],
        })
        assert not is_short_porch_hr(df).iloc[0]


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
