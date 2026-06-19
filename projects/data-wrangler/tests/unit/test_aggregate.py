"""Unit tests for datawrangler.aggregate."""

import pandas as pd
import pytest

from datawrangler.aggregate import group_summary, pivot_summary, rolling_stats


class TestGroupSummary:
    def test_single_agg(self, sales_df: pd.DataFrame) -> None:
        result = group_summary(sales_df, by=["region"], agg={"sales": "sum"})
        assert "region" in result.columns
        assert "sales" in result.columns
        north = result[result["region"] == "North"]["sales"].iloc[0]
        assert north == pytest.approx(300.0)

    def test_multi_agg_flat_columns(self, sales_df: pd.DataFrame) -> None:
        result = group_summary(sales_df, by=["region"], agg={"sales": ["min", "max"]})
        assert "sales_min" in result.columns or "sales" in result.columns

    def test_multi_group_by(self, sales_df: pd.DataFrame) -> None:
        result = group_summary(sales_df, by=["region", "product"], agg={"qty": "sum"})
        assert len(result) == 4

    def test_result_reset_index(self, sales_df: pd.DataFrame) -> None:
        result = group_summary(sales_df, by=["region"], agg={"sales": "sum"})
        assert isinstance(result.index, pd.RangeIndex)


class TestRollingStats:
    def test_default_stats_columns(self, numeric_df: pd.DataFrame) -> None:
        result = rolling_stats(numeric_df, column="a", window=3)
        assert "a_rolling_mean" in result.columns
        assert "a_rolling_std" in result.columns
        assert "a_rolling_min" in result.columns
        assert "a_rolling_max" in result.columns

    def test_custom_stats(self, numeric_df: pd.DataFrame) -> None:
        result = rolling_stats(numeric_df, column="a", window=2, stats=["mean"])
        assert "a_rolling_mean" in result.columns
        assert "a_rolling_std" not in result.columns

    def test_missing_column_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(KeyError, match="nonexistent"):
            rolling_stats(numeric_df, column="nonexistent", window=2)

    def test_invalid_window_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="window must be"):
            rolling_stats(numeric_df, column="a", window=0)

    def test_invalid_stat_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="not available"):
            rolling_stats(numeric_df, column="a", window=2, stats=["not_a_stat"])

    def test_original_column_preserved(self, numeric_df: pd.DataFrame) -> None:
        result = rolling_stats(numeric_df, column="a", window=2)
        pd.testing.assert_series_equal(result["a"], numeric_df["a"])


class TestPivotSummary:
    def test_pivot_shape(self, sales_df: pd.DataFrame) -> None:
        result = pivot_summary(sales_df, index="region", columns="product", values="sales")
        assert "region" in result.columns
        assert "A" in result.columns
        assert "B" in result.columns

    def test_pivot_sum(self, sales_df: pd.DataFrame) -> None:
        result = pivot_summary(sales_df, index="region", columns="product", values="sales", aggfunc="sum")
        north_a = result[result["region"] == "North"]["A"].iloc[0]
        assert north_a == pytest.approx(100.0)

    def test_reset_index(self, sales_df: pd.DataFrame) -> None:
        result = pivot_summary(sales_df, index="region", columns="product", values="sales")
        assert isinstance(result.index, pd.RangeIndex)
