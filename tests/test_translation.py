"""Tests for tools-to-production translation gap calculation."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.translation import (
    compute_results_score,
    compute_translation_gap,
)


class TestComputeResultsScore:
    def test_returns_expected_keys(self):
        batting = pd.DataFrame({
            "Name": ["Anthony Volpe"],
            "wOBA": [0.300],
            "wRC+": [95],
            "OPS": [0.700],
        })
        result = compute_results_score(batting, "Anthony Volpe")
        assert "woba" in result
        assert "wrc_plus" in result
        assert "ops" in result

    def test_correct_values(self):
        batting = pd.DataFrame({
            "Name": ["Test Player"],
            "wOBA": [0.350],
            "wRC+": [120],
            "OPS": [0.800],
        })
        result = compute_results_score(batting, "Test Player")
        assert result["woba"] == 0.350
        assert result["wrc_plus"] == 120
        assert result["ops"] == 0.800

    def test_missing_player_returns_nans(self):
        batting = pd.DataFrame({
            "Name": ["Other Player"],
            "wOBA": [0.300],
            "wRC+": [95],
            "OPS": [0.700],
        })
        result = compute_results_score(batting, "Nobody")
        assert np.isnan(result["woba"])

    def test_multiple_players_returns_first(self):
        batting = pd.DataFrame({
            "Name": ["Player A", "Player A"],
            "wOBA": [0.300, 0.350],
            "wRC+": [95, 120],
            "OPS": [0.700, 0.800],
        })
        result = compute_results_score(batting, "Player A")
        assert result["woba"] == 0.300


class TestComputeTranslationGap:
    def _make_tools_and_results(self):
        tools = pd.DataFrame({
            "batter_id": [1, 2, 3],
            "tools_composite_z": [1.5, 0.0, -1.0],
        }).set_index("batter_id")

        results = pd.DataFrame({
            "batter_id": [1, 2, 3],
            "woba": [0.280, 0.330, 0.380],
            "wrc_plus": [85, 110, 135],
        }).set_index("batter_id")

        return tools, results

    def test_returns_dataframe(self):
        tools, results = self._make_tools_and_results()
        gap = compute_translation_gap(tools, results)
        assert isinstance(gap, pd.DataFrame)

    def test_positive_gap_means_underperforming(self):
        tools, results = self._make_tools_and_results()
        gap = compute_translation_gap(tools, results)
        # Batter 1: high tools (1.5), low results (0.280 wOBA) -> positive gap
        assert gap.loc[1, "translation_gap"] > 0

    def test_negative_gap_means_overperforming(self):
        tools, results = self._make_tools_and_results()
        gap = compute_translation_gap(tools, results)
        # Batter 3: low tools (-1.0), high results (0.380 wOBA) -> negative gap
        assert gap.loc[3, "translation_gap"] < 0

    def test_sorted_descending(self):
        tools, results = self._make_tools_and_results()
        gap = compute_translation_gap(tools, results)
        gaps = gap["translation_gap"].tolist()
        assert gaps == sorted(gaps, reverse=True)

    def test_z_scores_added(self):
        tools, results = self._make_tools_and_results()
        gap = compute_translation_gap(tools, results)
        assert "woba_z" in gap.columns
        assert "wrc_plus_z" in gap.columns

    def test_inner_join_on_shared_ids(self):
        tools = pd.DataFrame({
            "batter_id": [1, 2],
            "tools_composite_z": [1.0, -1.0],
        }).set_index("batter_id")

        results = pd.DataFrame({
            "batter_id": [2, 3],
            "woba": [0.330, 0.380],
            "wrc_plus": [110, 135],
        }).set_index("batter_id")

        gap = compute_translation_gap(tools, results)
        assert len(gap) == 1
        assert 2 in gap.index

    def test_zero_variance_handled(self):
        tools = pd.DataFrame({
            "batter_id": [1, 2],
            "tools_composite_z": [0.5, 0.5],
        }).set_index("batter_id")

        results = pd.DataFrame({
            "batter_id": [1, 2],
            "woba": [0.330, 0.330],
            "wrc_plus": [110, 110],
        }).set_index("batter_id")

        gap = compute_translation_gap(tools, results)
        # Should not raise — z-scores should be 0 with zero variance
        assert gap.loc[1, "woba_z"] == 0.0
