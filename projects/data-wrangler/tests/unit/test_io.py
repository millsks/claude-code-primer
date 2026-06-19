"""Unit tests for datawrangler.io — uses tmp_path, no real filesystem state left behind."""

import pandas as pd
import pytest

from datawrangler.io import read_csv, read_parquet, write_csv, write_parquet


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"name": ["alice", "bob"], "score": [90.0, 85.5]})


class TestCsvRoundtrip:
    def test_write_then_read(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "out.csv"  # type: ignore[operator]
        write_csv(sample_df, p)
        result = read_csv(p)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_creates_parent_dirs(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "subdir" / "nested" / "out.csv"  # type: ignore[operator]
        write_csv(sample_df, p)
        assert p.exists()  # type: ignore[union-attr]

    def test_no_index_by_default(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "out.csv"  # type: ignore[operator]
        write_csv(sample_df, p)
        raw = p.read_text()  # type: ignore[union-attr]
        assert "Unnamed" not in raw

    def test_read_kwargs_forwarded(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "out.csv"  # type: ignore[operator]
        write_csv(sample_df, p)
        result = read_csv(p, usecols=["name"])
        assert list(result.columns) == ["name"]


class TestParquetRoundtrip:
    def test_write_then_read(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "out.parquet"  # type: ignore[operator]
        write_parquet(sample_df, p)
        result = read_parquet(p)
        pd.testing.assert_frame_equal(result, sample_df)

    def test_column_projection(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "out.parquet"  # type: ignore[operator]
        write_parquet(sample_df, p)
        result = read_parquet(p, columns=["name"])
        assert list(result.columns) == ["name"]

    def test_creates_parent_dirs(self, sample_df: pd.DataFrame, tmp_path: pytest.TempPathFactory) -> None:
        p = tmp_path / "sub" / "out.parquet"  # type: ignore[operator]
        write_parquet(sample_df, p)
        assert p.exists()  # type: ignore[union-attr]
