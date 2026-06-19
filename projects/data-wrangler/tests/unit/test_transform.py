"""Unit tests for datawrangler.transform."""

import pandas as pd
import pytest

from datawrangler.transform import encode_categoricals, normalize, reshape_wide_to_long


class TestNormalize:
    def test_minmax_range(self, numeric_df: pd.DataFrame) -> None:
        result = normalize(numeric_df, columns=["a"], method="minmax")
        assert result["a"].min() == pytest.approx(0.0)
        assert result["a"].max() == pytest.approx(1.0)

    def test_zscore_mean_std(self, numeric_df: pd.DataFrame) -> None:
        result = normalize(numeric_df, columns=["a"], method="zscore")
        assert result["a"].mean() == pytest.approx(0.0, abs=1e-10)
        assert result["a"].std() == pytest.approx(1.0, abs=1e-10)

    def test_untouched_columns_unchanged(self, numeric_df: pd.DataFrame) -> None:
        result = normalize(numeric_df, columns=["a"], method="minmax")
        pd.testing.assert_series_equal(result["b"], numeric_df["b"])

    def test_zero_range_column_unchanged(self) -> None:
        df = pd.DataFrame({"flat": [5.0, 5.0, 5.0]})
        result = normalize(df, columns=["flat"], method="minmax")
        pd.testing.assert_series_equal(result["flat"], df["flat"])

    def test_zero_std_column_unchanged(self) -> None:
        df = pd.DataFrame({"flat": [5.0, 5.0, 5.0]})
        result = normalize(df, columns=["flat"], method="zscore")
        pd.testing.assert_series_equal(result["flat"], df["flat"])

    def test_unknown_method_raises(self, numeric_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="method must be"):
            normalize(numeric_df, columns=["a"], method="bad")

    def test_missing_column_skipped(self, numeric_df: pd.DataFrame) -> None:
        result = normalize(numeric_df, columns=["nonexistent"], method="minmax")
        pd.testing.assert_frame_equal(result, numeric_df)


class TestEncodeCategorials:
    def test_onehot_creates_indicator_columns(self, categorical_df: pd.DataFrame) -> None:
        result = encode_categoricals(categorical_df, columns=["color"], method="onehot")
        assert "color" not in result.columns
        assert "color_red" in result.columns
        assert "color_blue" in result.columns

    def test_label_encoding_integer_codes(self, categorical_df: pd.DataFrame) -> None:
        result = encode_categoricals(categorical_df, columns=["color"], method="label")
        assert "color" in result.columns
        assert result["color"].dtype.kind in ("i", "u")

    def test_unknown_method_raises(self, categorical_df: pd.DataFrame) -> None:
        with pytest.raises(ValueError, match="method must be"):
            encode_categoricals(categorical_df, columns=["color"], method="bad")

    def test_missing_column_skipped(self, categorical_df: pd.DataFrame) -> None:
        result = encode_categoricals(categorical_df, columns=["nonexistent"], method="onehot")
        assert list(result.columns) == list(categorical_df.columns)


class TestReshapeWideLong:
    def test_basic_melt(self) -> None:
        df = pd.DataFrame({"id": [1, 2], "jan": [100, 200], "feb": [150, 250]})
        result = reshape_wide_to_long(df, id_vars=["id"], value_vars=["jan", "feb"])
        assert len(result) == 4
        assert "variable" in result.columns
        assert "value" in result.columns

    def test_custom_names(self) -> None:
        df = pd.DataFrame({"id": [1], "q1": [10], "q2": [20]})
        result = reshape_wide_to_long(df, id_vars=["id"], value_vars=["q1", "q2"], var_name="quarter", value_name="revenue")
        assert "quarter" in result.columns
        assert "revenue" in result.columns

    def test_row_count(self) -> None:
        df = pd.DataFrame({"id": [1, 2, 3], "x": [1, 2, 3], "y": [4, 5, 6]})
        result = reshape_wide_to_long(df, id_vars=["id"], value_vars=["x", "y"])
        assert len(result) == 6
