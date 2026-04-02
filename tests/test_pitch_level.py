"""Tests for pitch-level feature engineering."""

import numpy as np
import pandas as pd
import pytest

from fire_fishman.features.pitch_level import (
    PITCH_GROUPS,
    _classify_pitch,
    _is_swing,
    _is_whiff,
    _is_in_zone,
    _parse_count,
    compute_plate_discipline,
    compute_whiff_by_pitch_type,
    compute_count_performance,
)


# --- Unit tests for classification helpers ---


class TestClassifyPitch:
    def test_fastball_types(self):
        assert _classify_pitch("FF") == "fastball"
        assert _classify_pitch("SI") == "fastball"
        assert _classify_pitch("FC") == "fastball"

    def test_breaking_types(self):
        assert _classify_pitch("SL") == "breaking"
        assert _classify_pitch("CU") == "breaking"
        assert _classify_pitch("SV") == "breaking"

    def test_offspeed_types(self):
        assert _classify_pitch("CH") == "offspeed"
        assert _classify_pitch("FS") == "offspeed"

    def test_unknown_returns_other(self):
        assert _classify_pitch("KN") == "other"
        assert _classify_pitch("XX") == "other"


class TestIsSwing:
    def test_swing_descriptions(self):
        assert _is_swing("swinging_strike") is True
        assert _is_swing("foul") is True
        assert _is_swing("hit_into_play") is True
        assert _is_swing("foul_tip") is True

    def test_non_swing_descriptions(self):
        assert _is_swing("called_strike") is False
        assert _is_swing("ball") is False
        assert _is_swing("blocked_ball") is False


class TestIsWhiff:
    def test_whiff_descriptions(self):
        assert _is_whiff("swinging_strike") is True
        assert _is_whiff("swinging_strike_blocked") is True

    def test_non_whiff(self):
        assert _is_whiff("foul") is False
        assert _is_whiff("hit_into_play") is False
        assert _is_whiff("called_strike") is False


class TestIsInZone:
    def test_center_of_zone(self):
        assert _is_in_zone(0.0, 2.5, 3.5, 1.5) is True

    def test_outside_horizontally(self):
        assert _is_in_zone(1.0, 2.5, 3.5, 1.5) is False  # outside right
        assert _is_in_zone(-1.0, 2.5, 3.5, 1.5) is False  # outside left

    def test_above_zone(self):
        assert _is_in_zone(0.0, 4.0, 3.5, 1.5) is False

    def test_below_zone(self):
        assert _is_in_zone(0.0, 1.0, 3.5, 1.5) is False

    def test_on_edge(self):
        # Exactly on the boundary should be in zone
        assert _is_in_zone(0.83, 2.5, 3.5, 1.5) is True
        assert _is_in_zone(-0.83, 2.5, 3.5, 1.5) is True


class TestParseCount:
    def test_two_strike(self):
        assert _parse_count(0, 2) == "two_strike"
        assert _parse_count(3, 2) == "two_strike"

    def test_hitter_ahead(self):
        assert _parse_count(2, 0) == "hitter_ahead"
        assert _parse_count(3, 1) == "hitter_ahead"

    def test_pitcher_ahead(self):
        assert _parse_count(0, 1) == "pitcher_ahead"

    def test_even(self):
        assert _parse_count(1, 1) == "even"
        assert _parse_count(0, 0) == "even"


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

    return pd.DataFrame({
        "batter": batter_id,
        "description": descriptions,
        "pitch_type": pitch_types,
        "plate_x": plate_x,
        "plate_z": plate_z,
        "sz_top": 3.5,
        "sz_bot": 1.5,
        "release_speed": rng.uniform(85, 100, size=n),
        "launch_speed": rng.choice([np.nan, 90, 95, 100, 105], size=n),
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
