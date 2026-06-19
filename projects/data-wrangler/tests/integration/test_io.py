"""Integration tests — full pipeline from file I/O through transforms and aggregation."""

import pytest

from datawrangler.aggregate import group_summary
from datawrangler.io import read_csv, write_csv, write_parquet, read_parquet
from datawrangler.transform import normalize, reshape_wide_to_long


@pytest.mark.integration
def test_csv_load_reshape_aggregate(wide_sales_csv: str, tmp_path: pytest.TempPathFactory) -> None:
    """Read CSV → reshape wide→long → aggregate → write CSV → reload and verify."""
    df = read_csv(wide_sales_csv)
    assert len(df) == 20

    long_df = reshape_wide_to_long(df, id_vars=["region", "product"], value_vars=["q1", "q2"], var_name="quarter", value_name="revenue")
    assert len(long_df) == 40
    assert "quarter" in long_df.columns

    summary = group_summary(long_df, by=["region", "quarter"], agg={"revenue": "sum"})
    assert "revenue" in summary.columns
    assert len(summary) == 8  # 4 regions × 2 quarters

    out = tmp_path / "summary.csv"  # type: ignore[operator]
    write_csv(summary, out)
    reloaded = read_csv(out)
    assert list(reloaded.columns) == list(summary.columns)
    assert len(reloaded) == len(summary)


@pytest.mark.integration
def test_parquet_roundtrip_with_normalization(wide_sales_csv: str, tmp_path: pytest.TempPathFactory) -> None:
    """Read CSV → normalize → write parquet → reload and verify bounds."""
    df = read_csv(wide_sales_csv)
    normalized = normalize(df, columns=["q1", "q2"], method="minmax")

    assert normalized["q1"].min() >= 0.0
    assert normalized["q1"].max() <= 1.0

    pq_path = tmp_path / "normalized.parquet"  # type: ignore[operator]
    write_parquet(normalized, pq_path)
    reloaded = read_parquet(pq_path, columns=["q1", "q2"])

    assert reloaded["q1"].min() >= 0.0
    assert reloaded["q1"].max() <= 1.0
