"""Aggregation utilities."""

from __future__ import annotations

import pandas as pd
import structlog

log = structlog.get_logger()


def group_summary(
    df: pd.DataFrame,
    by: list[str],
    agg: dict[str, str | list[str]],
) -> pd.DataFrame:
    """Group a DataFrame and compute per-group aggregations.

    Args:
        df: Input DataFrame.
        by: Column names to group by.
        agg: Mapping of column name to aggregation function(s), e.g.
            ``{"sales": "sum", "qty": ["min", "max"]}``. Any function accepted
            by :meth:`pandas.core.groupby.DataFrameGroupBy.agg` is valid.

    Returns:
        Aggregated DataFrame with a flat column index and the group-by columns
        reset to regular columns.
    """
    result: pd.DataFrame = df.groupby(by).agg(agg)  # type: ignore[arg-type]
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ["_".join(parts).strip("_") for parts in result.columns]
    return result.reset_index()


def rolling_stats(
    df: pd.DataFrame,
    column: str,
    window: int,
    stats: list[str] | None = None,
) -> pd.DataFrame:
    """Compute rolling statistics for a single numeric column.

    Args:
        df: Input DataFrame (must be sorted by the relevant time or sequence axis beforehand).
        column: Name of the column to compute rolling statistics on.
        window: Number of rows in the rolling window.
        stats: Statistics to compute. Defaults to ``["mean", "std", "min", "max"]``.
            Any method name available on :class:`pandas.core.window.rolling.Rolling` works.

    Returns:
        DataFrame containing the original column plus ``<column>_rolling_<stat>`` columns
        for each requested statistic.

    Raises:
        KeyError: If column is not in df.
        ValueError: If window is less than 1 or a requested stat is not available.
    """
    if column not in df.columns:
        raise KeyError(f"Column {column!r} not in DataFrame")
    if window < 1:
        raise ValueError(f"window must be >= 1, got {window}")

    target_stats = stats or ["mean", "std", "min", "max"]
    rolling = df[column].rolling(window=window)
    result = df.copy()

    for stat in target_stats:
        if not hasattr(rolling, stat):
            raise ValueError(f"Rolling statistic {stat!r} is not available")
        result[f"{column}_rolling_{stat}"] = getattr(rolling, stat)()

    return result


def pivot_summary(
    df: pd.DataFrame,
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "mean",
) -> pd.DataFrame:
    """Build a pivot table with a single aggregation function.

    Args:
        df: Input DataFrame.
        index: Column to use as row labels.
        columns: Column whose unique values become the column headers.
        values: Column to aggregate.
        aggfunc: Aggregation function name understood by :func:`pandas.pivot_table`,
            e.g. ``"mean"``, ``"sum"``, ``"count"``.

    Returns:
        Pivot table as a DataFrame with the index column reset to a regular column.
    """
    result = pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=aggfunc)
    result.columns.name = None
    return result.reset_index()
