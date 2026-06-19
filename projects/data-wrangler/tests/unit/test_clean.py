"""Unit tests for datawrangler.clean."""

import numpy as np
import pandas as pd
import pytest

from datawrangler.clean import cast_dtypes, clip_outliers, drop_duplicates, fill_nulls


class TestDropDuplicates:
    def test_removes_exact_duplicates(self) -> None:
        df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
        result = drop_duplicates(df)
        assert len(result) == 2

    def test_subset_dedup(self) -> None:
        df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 9, 4]})
        result = drop_duplicates(df, subset=["a"])
        assert len(result) == 2

    def test_keep_last(self) -> None:
        df = pd.DataFrame({"a": [1, 1], "b": [10, 20]})
        result = drop_duplicates(df, subset=["a"], keep="last")
        assert result.iloc[0]["b"] == 20

    def test_no_duplicates_unchanged(self, numeric_df: pd.DataFrame) -> None:
        result = drop_duplicates(numeric_df)
        assert len(result) == len(numeric_df)


class TestFillNulls:
    def test_mean_strategy(self, df_with_nulls: pd.DataFrame) -> None:
        result = fill_nulls(df_with_nulls, strategy="mean")
        assert result.isna().sum().sum() == 0
        assert result["x"].iloc[1] == pytest.approx((1.0 + 3.0 + 5.0) / 3)

    def test_median_strategy(self, df_with_nulls: pd.DataFrame) -> None:
        result = fill_nulls(df_with_nulls, strategy="median")
        assert result.isna().sum().sum() == 0

    def test_mode_strategy(self) -> None:
        df = pd.DataFrame({"v": [1.0, 1.0, np.nan, 2.0]})
        result = fill_nulls(df, strategy="mode")
        assert result["v"].iloc[2] == 1.0

    def test_constant_strategy(self, df_with_nulls: pd.DataFrame) -> None:
        result = fill_nulls(df_with_nulls, strategy="constant", fill_value=0.0)
        assert result.isna().sum().sum() == 0
        assert (result == 0.0).any().any()

    def test_specific_columns(self, df_with_nulls: pd.DataFrame) -> None:
        result = fill_nulls(df_with_nulls, strategy="mean", columns=["x"])
        assert result["x"].isna().sum() == 0
        assert result["y"].isna().sum() > 0

    def test_unknown_strategy_raises(self, df_with_nulls: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="strategy must be"):
            fill_nulls(df_with_nulls, strategy="bad")

    def test_constant_without_value_raises(self, df_with_nulls: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="fill_value is required"):
            fill_nulls(df_with_nulls, strategy="constant")

    def test_no_nulls_unchanged(self, numeric_df: pd.DataFrame) -> None:
        result = fill_nulls(numeric_df)
        pd.testing.assert_frame_equal(result, numeric_df)

    def test_missing_column_skipped(self, df_with_nulls: pd.DataFrame) -> None:
        result = fill_nulls(df_with_nulls, strategy="mean", columns=["nonexistent"])
        pd.testing.assert_frame_equal(result, df_with_nulls)


class TestCastDtypes:
    def test_cast_float_to_int(self, numeric_df: pd.DataFrame) -> None:
        result = cast_dtypes(numeric_df, {"a": "int64"})
        assert result["a"].dtype == "int64"

    def test_cast_to_string(self, numeric_df: pd.DataFrame) -> None:
        result = cast_dtypes(numeric_df, {"a": "str"})
        assert result["a"].dtype == object

    def test_missing_column_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(KeyError, match="nonexistent"):
            cast_dtypes(numeric_df, {"nonexistent": "int64"})

    def test_bad_cast_raises(self) -> None:
        df = pd.DataFrame({"v": ["hello", "world"]})
        with pytest.raises(ValueError, match="Cannot cast"):
            cast_dtypes(df, {"v": "float64"})


class TestClipOutliers:
    def test_iqr_clips_extremes(self) -> None:
        df = pd.DataFrame({"v": [1.0, 2.0, 3.0, 4.0, 100.0]})
        result = clip_outliers(df, columns=["v"], method="iqr", factor=1.5)
        assert result["v"].iloc[-1] < 100.0

    def test_zscore_clips_extremes(self) -> None:
        df = pd.DataFrame({"v": [1.0, 2.0, 3.0, 4.0, 100.0]})
        result = clip_outliers(df, columns=["v"], method="zscore", factor=2.0)
        assert result["v"].iloc[-1] < 100.0

    def test_no_outliers_unchanged(self, numeric_df: pd.DataFrame) -> None:
        result = clip_outliers(numeric_df, columns=["a"], method="iqr", factor=3.0)
        pd.testing.assert_series_equal(result["a"], numeric_df["a"])

    def test_unknown_method_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="method must be"):
            clip_outliers(numeric_df, columns=["a"], method="bad")

    def test_missing_column_skipped(self, numeric_df: pd.DataFrame) -> None:
        result = clip_outliers(numeric_df, columns=["nonexistent"])
        pd.testing.assert_frame_equal(result, numeric_df)
