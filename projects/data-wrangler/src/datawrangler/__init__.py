"""Data wrangling and analysis utilities."""

from datawrangler.aggregate import group_summary, pivot_summary, rolling_stats
from datawrangler.clean import cast_dtypes, clip_outliers, drop_duplicates, fill_nulls
from datawrangler.io import read_csv, read_excel, read_parquet, write_csv, write_parquet
from datawrangler.transform import encode_categoricals, normalize, reshape_wide_to_long

__version__ = "0.1.0"

__all__ = [
    # clean
    "cast_dtypes",
    "clip_outliers",
    "drop_duplicates",
    "fill_nulls",
    # transform
    "encode_categoricals",
    "normalize",
    "reshape_wide_to_long",
    # aggregate
    "group_summary",
    "pivot_summary",
    "rolling_stats",
    # io
    "read_csv",
    "read_excel",
    "read_parquet",
    "write_csv",
    "write_parquet",
]
