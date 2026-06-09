"""Tests for the team value composite (notebooks 08/09 shared definition)."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.team_value import (
    FG_TEAM_NAME_TO_ABBR,
    compute_value_composite,
    merge_team_batting_fielding,
)


def _make_merged(n_teams=6, seasons=(2023, 2024), seed=42):
    rng = np.random.RandomState(seed)
    rows = []
    for season in seasons:
        for i in range(n_teams):
            rows.append({
                "Season": season,
                "Team": f"T{i}",
                "+WPA": rng.uniform(20, 40),
                "-WPA": rng.uniform(-40, -20),
                "UBR": rng.uniform(-10, 10),
                "BsR": rng.uniform(-15, 15),
                "OAA": rng.uniform(-30, 30),
                "WAR": rng.uniform(10, 50),
            })
    return pd.DataFrame(rows)


class TestTeamNameMap:
    def test_uses_fangraphs_batting_abbreviations(self):
        # The FanGraphs batting endpoint uses TBR/WSN/CHW. The old notebook
        # maps emitted TB/WSH/CWS, silently dropping three teams per season.
        assert FG_TEAM_NAME_TO_ABBR["Rays"] == "TBR"
        assert FG_TEAM_NAME_TO_ABBR["Nationals"] == "WSN"
        assert FG_TEAM_NAME_TO_ABBR["White Sox"] == "CHW"

    def test_covers_30_franchises(self):
        # Aliases (Indians/Guardians/Cleveland, Rays/Tampa Bay) collapse to
        # exactly 30 distinct abbreviations.
        assert len(set(FG_TEAM_NAME_TO_ABBR.values())) == 30


class TestMergeTeamBattingFielding:
    def _frames(self):
        batting = pd.DataFrame({
            "Season": [2024, 2024],
            "Team": ["NYY", "TBR"],
            "WAR": [40.0, 30.0],
        })
        fielding = pd.DataFrame({
            "Season": [2024, 2024],
            "Team": ["Yankees", "Rays"],
            "OAA": [10.0, 20.0],
            "DRS": [5.0, 15.0],
        })
        return batting, fielding

    def test_merges_all_teams(self):
        batting, fielding = self._frames()
        merged = merge_team_batting_fielding(batting, fielding)
        assert len(merged) == 2
        assert merged["OAA"].notna().all()

    def test_raises_on_unmapped_fielding_label(self):
        batting, fielding = self._frames()
        fielding.loc[1, "Team"] = "Devil Rays"
        with pytest.raises(ValueError, match="Unmapped"):
            merge_team_batting_fielding(batting, fielding)

    def test_raises_when_merge_drops_a_team(self):
        batting, fielding = self._frames()
        fielding = fielding.iloc[:1]  # no Rays fielding row
        with pytest.raises(ValueError, match="dropped OAA"):
            merge_team_batting_fielding(batting, fielding)


class TestComputeValueComposite:
    def test_adds_expected_columns(self):
        df = compute_value_composite(_make_merged())
        for col in ["pressure", "hustle", "grit", "value_composite"]:
            assert col in df.columns

    def test_z_scores_centered_within_season(self):
        df = compute_value_composite(_make_merged(n_teams=10))
        for _, season_df in df.groupby("Season"):
            assert season_df["OAA_z"].mean() == pytest.approx(0.0, abs=1e-9)

    def test_equal_weights_average_components(self):
        df = compute_value_composite(_make_merged())
        expected = (df["pressure"] + df["hustle"] + df["grit"]) / 3
        pd.testing.assert_series_equal(
            df["value_composite"], expected, check_names=False
        )

    def test_neg_wpa_direction_matches_notebook_definition(self):
        # The original notebook definition z-scores -WPA with direction -1:
        # larger negative-WPA volume scores HIGHER. This is what keeps the
        # pressure component near-orthogonal to wRC+ (see module docstring),
        # so the consolidation preserves it. This test locks the convention
        # so a future "fix" doesn't silently redefine the published metric.
        merged = _make_merged(n_teams=4, seasons=(2024,))
        merged["-WPA"] = [-40.0, -30.0, -20.0, -10.0]
        df = compute_value_composite(merged).sort_values("-WPA")
        assert df["-WPA_z"].is_monotonic_decreasing

    def test_custom_weights(self):
        df = compute_value_composite(_make_merged(), weights=(0.5, 0.25, 0.25))
        expected = 0.5 * df["pressure"] + 0.25 * df["hustle"] + 0.25 * df["grit"]
        pd.testing.assert_series_equal(
            df["value_composite"], expected, check_names=False
        )

    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValueError, match="sum to 1"):
            compute_value_composite(_make_merged(), weights=(0.5, 0.5, 0.5))
