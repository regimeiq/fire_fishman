"""Tests for prospect data integrity."""

import pandas as pd
import pytest

from fire_fishman.data.prospects import (
    PROSPECT_DATA,
    MILB_STATS,
    FANGRAPHS_IDS,
    YANKEES_SYSTEM,
    get_prospect_df,
    get_prospect_ids,
    get_yankees_prospects,
    get_yankees_system_df,
)


class TestProspectData:
    def test_prospect_data_not_empty(self):
        assert len(PROSPECT_DATA) > 0

    def test_prospect_tuple_format(self):
        for entry in PROSPECT_DATA:
            name, mlbam_id, debut_year, rank, outcome = entry
            assert isinstance(name, str)
            assert isinstance(mlbam_id, int)
            assert 2019 <= debut_year <= 2025
            assert 1 <= rank <= 100
            assert outcome in ("star", "solid", "disappointing", "bust")

    def test_no_duplicate_names(self):
        names = [name for name, *_ in PROSPECT_DATA]
        assert len(names) == len(set(names)), f"Duplicates: {[n for n in names if names.count(n) > 1]}"

    def test_no_duplicate_mlbam_ids(self):
        ids = [mid for _, mid, *_ in PROSPECT_DATA]
        assert len(ids) == len(set(ids))


class TestGetProspectDf:
    def test_returns_dataframe(self):
        df = get_prospect_df()
        assert isinstance(df, pd.DataFrame)

    def test_expected_columns(self):
        df = get_prospect_df()
        expected = {"name", "mlbam_id", "debut_year", "pre_debut_rank", "outcome"}
        assert set(df.columns) == expected

    def test_row_count_matches(self):
        df = get_prospect_df()
        assert len(df) == len(PROSPECT_DATA)


class TestGetProspectIds:
    def test_returns_dict(self):
        ids = get_prospect_ids()
        assert isinstance(ids, dict)
        assert all(isinstance(v, int) for v in ids.values())

    def test_key_players_present(self):
        ids = get_prospect_ids()
        assert "Anthony Volpe" in ids
        assert "Gunnar Henderson" in ids
        assert "Bobby Witt Jr." in ids


class TestYankeesProspects:
    def test_returns_three(self):
        df = get_yankees_prospects()
        assert len(df) == 3
        assert set(df["name"]) == {"Anthony Volpe", "Jasson Dominguez", "Ben Rice"}

    def test_system_includes_expanded(self):
        df = get_yankees_system_df()
        assert len(df) >= 5
        names = set(df["name"])
        assert "Austin Wells" in names
        assert "Oswald Peraza" in names


class TestMilbStats:
    def test_yankees_core_present(self):
        assert "Anthony Volpe" in MILB_STATS
        assert "Jasson Dominguez" in MILB_STATS
        assert "Ben Rice" in MILB_STATS

    def test_stat_fields(self):
        for player, seasons in MILB_STATS.items():
            for year, stats in seasons.items():
                assert "level" in stats, f"{player} {year} missing level"
                assert "pa" in stats, f"{player} {year} missing pa"
                assert "bb_pct" in stats, f"{player} {year} missing bb_pct"
                assert "k_pct" in stats, f"{player} {year} missing k_pct"

    def test_rates_are_valid(self):
        for player, seasons in MILB_STATS.items():
            for year, stats in seasons.items():
                assert 0 < stats["bb_pct"] < 0.30, f"{player} {year} bb_pct={stats['bb_pct']}"
                assert 0 < stats["k_pct"] < 0.50, f"{player} {year} k_pct={stats['k_pct']}"


class TestFangraphsIds:
    def test_ids_are_positive_ints(self):
        for name, fid in FANGRAPHS_IDS.items():
            assert isinstance(fid, int) and fid > 0, f"{name}: {fid}"

    def test_core_players_present(self):
        assert "Anthony Volpe" in FANGRAPHS_IDS
        assert "Ben Rice" in FANGRAPHS_IDS
        assert "Aaron Judge" not in FANGRAPHS_IDS  # only prospects tracked
