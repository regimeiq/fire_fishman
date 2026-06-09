"""Tests for pitch-level feature engineering."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.pitch_level import (
    _vectorized_zone_swing_whiff,
    compute_all_pitch_features,
    compute_plate_discipline,
    compute_whiff_by_pitch_type,
    compute_count_performance,
    compute_pitch_features_for_cohort,
)


# --- Unit tests for the vectorized classification helper ---


class TestVectorizedZoneSwingWhiff:
    def _frame(self, **overrides):
        base = {
            "description": ["called_strike"],
            "pitch_type": ["FF"],
            "plate_x": [0.0],
            "plate_z": [2.5],
            "sz_top": [3.5],
            "sz_bot": [1.5],
        }
        base.update(overrides)
        return pd.DataFrame(base)

    def test_swing_and_whiff_classification(self):
        df = self._frame(
            description=["swinging_strike", "foul", "hit_into_play", "called_strike", "ball"],
            pitch_type=["FF"] * 5,
            plate_x=[0.0] * 5, plate_z=[2.5] * 5, sz_top=[3.5] * 5, sz_bot=[1.5] * 5,
        )
        out = _vectorized_zone_swing_whiff(df)
        assert out["is_swing"].tolist() == [True, True, True, False, False]
        assert out["is_whiff"].tolist() == [True, False, False, False, False]

    def test_pitch_group_mapping(self):
        df = self._frame(
            description=["ball"] * 6,
            pitch_type=["FF", "SI", "SL", "CU", "CH", "KN"],
            plate_x=[0.0] * 6, plate_z=[2.5] * 6, sz_top=[3.5] * 6, sz_bot=[1.5] * 6,
        )
        out = _vectorized_zone_swing_whiff(df)
        assert out["pitch_group"].tolist() == [
            "fastball", "fastball", "breaking", "breaking", "offspeed", "other"
        ]

    def test_zone_classification(self):
        df = self._frame(
            description=["ball"] * 5,
            pitch_type=["FF"] * 5,
            plate_x=[0.0, 1.0, 0.0, 0.0, 0.83],
            plate_z=[2.5, 2.5, 4.0, 1.0, 2.5],
            sz_top=[3.5] * 5, sz_bot=[1.5] * 5,
        )
        out = _vectorized_zone_swing_whiff(df)
        # center, outside right, above, below, on the edge (inclusive)
        assert out["in_zone"].tolist() == [True, False, False, False, True]

    def test_unknown_zone_flagged(self):
        df = self._frame(plate_x=[np.nan])
        out = _vectorized_zone_swing_whiff(df)
        assert not out["zone_known"].iloc[0]
        assert not out["in_zone"].iloc[0]


# --- Integration tests with synthetic pitch data ---


def _make_pitches(n=100, batter_id=12345, seed=42):
    """Create synthetic pitch data for testing."""
    rng = np.random.RandomState(seed)
    descriptions = rng.choice(
        ["swinging_strike", "foul", "hit_into_play", "called_strike", "ball"],
        size=n,
        p=[0.15, 0.20, 0.15, 0.25, 0.25],
    )
    pitch_types = rng.choice(["FF", "SL", "CH", "CU", "SI"], size=n)
    plate_x = rng.uniform(-1.5, 1.5, size=n)
    plate_z = rng.uniform(0.5, 4.5, size=n)
    # Statcast type code: X = in play, B = ball, S = strike (incl. fouls).
    # Launch readings exist on fouls too, so avg-EV metrics must filter type.
    types = np.select(
        [descriptions == "hit_into_play", descriptions == "ball"],
        ["X", "B"],
        default="S",
    )

    return pd.DataFrame({
        "batter": batter_id,
        "description": descriptions,
        "pitch_type": pitch_types,
        "type": types,
        "plate_x": plate_x,
        "plate_z": plate_z,
        "sz_top": 3.5,
        "sz_bot": 1.5,
        "release_speed": rng.uniform(85, 100, size=n),
        "launch_speed": np.where(
            np.isin(descriptions, ["hit_into_play", "foul"]),
            rng.choice([90, 95, 100, 105], size=n),
            np.nan,
        ),
        "balls": rng.randint(0, 4, size=n),
        "strikes": rng.randint(0, 3, size=n),
        "game_date": "2024-06-15",
    })


class TestComputePlateDiscipline:
    def test_returns_expected_keys(self):
        pitches = _make_pitches()
        result = compute_plate_discipline(pitches, 12345)
        assert "chase_rate" in result
        assert "zone_swing_rate" in result
        assert "zone_contact_rate" in result
        assert "whiff_rate" in result
        assert "total_pitches_seen" in result

    def test_rates_are_valid(self):
        pitches = _make_pitches(n=500)
        result = compute_plate_discipline(pitches, 12345)
        for key in ["chase_rate", "zone_swing_rate", "whiff_rate"]:
            assert 0 <= result[key] <= 1, f"{key} out of range: {result[key]}"

    def test_empty_batter_returns_empty(self):
        pitches = _make_pitches()
        result = compute_plate_discipline(pitches, 99999)
        assert result == {}

    def test_total_pitches(self):
        pitches = _make_pitches(n=200)
        result = compute_plate_discipline(pitches, 12345)
        assert result["total_pitches_seen"] == 200

    def test_missing_zone_coordinates_excluded_from_chase_denominator(self):
        pitches = pd.DataFrame({
            "batter": [12345, 12345],
            "description": ["foul", "called_strike"],
            "pitch_type": ["FF", "FF"],
            "plate_x": [np.nan, 1.2],
            "plate_z": [2.5, 2.5],
            "sz_top": [3.5, 3.5],
            "sz_bot": [1.5, 1.5],
        })
        result = compute_plate_discipline(pitches, 12345)
        assert result["chase_rate"] == 0.0


class TestComputeWhiffByPitchType:
    def test_returns_all_groups(self):
        pitches = _make_pitches(n=500)
        result = compute_whiff_by_pitch_type(pitches, 12345)
        for group in ["fastball", "breaking", "offspeed"]:
            assert f"whiff_rate_{group}" in result
            assert f"chase_rate_{group}" in result

    def test_whiff_rates_are_valid(self):
        pitches = _make_pitches(n=500)
        result = compute_whiff_by_pitch_type(pitches, 12345)
        for key, val in result.items():
            if not np.isnan(val):
                assert 0 <= val <= 1, f"{key} out of range: {val}"


class TestComputeCountPerformance:
    def test_returns_all_situations(self):
        pitches = _make_pitches(n=500)
        result = compute_count_performance(pitches, 12345)
        for sit in ["two_strike", "hitter_ahead", "pitcher_ahead", "even"]:
            assert f"whiff_rate_{sit}" in result


class TestComputePitchFeaturesForCohort:
    def test_vectorized_matches_single_batter_functions(self):
        pitches = pd.concat(
            [_make_pitches(n=500, batter_id=12345), _make_pitches(n=500, batter_id=67890, seed=7)]
        )
        cohort = compute_pitch_features_for_cohort(pitches, [12345, 67890])
        scalar = compute_all_pitch_features(pitches, 12345)

        for key, expected in scalar.items():
            actual = cohort.loc[12345, key]
            if np.isnan(expected):
                assert np.isnan(actual)
            else:
                assert actual == pytest.approx(expected)
