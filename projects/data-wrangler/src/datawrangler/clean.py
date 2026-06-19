"""Data cleaning utilities."""

from __future__ import annotations

import pandas as pd
import structlog

log = structlog.get_logger()


def drop_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> pd.DataFrame:
    """Remove duplicate rows from a DataFrame.

    Args:
        df: Input DataFrame.
        subset: Columns to consider when identifying duplicates. Uses all columns when None.
        keep: Which occurrence to keep — ``"first"``, ``"last"``, or ``False`` to drop all.

    Returns:
        DataFrame with duplicate rows removed.
    """
    before = len(df)
    result = df.drop_duplicates(subset=subset, keep=keep)  # type: ignore[arg-type]
    dropped = before - len(result)
    if dropped:
        log.info("dropped_duplicates", count=dropped)
    return result


def fill_nulls(
    df: pd.DataFrame,
    strategy: str = "mean",
    fill_value: float | str | None = None,
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """Fill null values using a descriptive or constant strategy.

    Args:
        df: Input DataFrame.
        strategy: One of ``"mean"``, ``"median"``, ``"mode"``, or ``"constant"``.
        fill_value: Scalar to use when ``strategy="constant"``.
        columns: Columns to fill. Defaults to all numeric columns when None.

    Returns:
        DataFrame with nulls filled per the chosen strategy.

    Raises:
        ValueError: If strategy is unknown or fill_value is absent for the constant strategy.
    """
    valid = {"mean", "median", "mode", "constant"}
    if strategy not in valid:
        raise ValueError(f"strategy must be one of {valid!r}, got {strategy!r}")
    if strategy == "constant" and fill_value is None:
        raise ValueError("fill_value is required when strategy='constant'")

    target_cols: list[str] = columns if columns is not None else df.select_dtypes(include="number").columns.tolist()
    result = df.copy()

    for col in target_cols:
        if col not in result.columns:
            continue
        null_count = int(result[col].isna().sum())
        if null_count == 0:
            continue
        if strategy == "mean":
            result[col] = result[col].fillna(result[col].mean())
        elif strategy == "median":
            result[col] = result[col].fillna(result[col].median())
        elif strategy == "mode":
            modes = result[col].mode()
            if len(modes):
                result[col] = result[col].fillna(modes.iloc[0])
        else:
            result[col] = result[col].fillna(fill_value)
        log.debug("filled_nulls", column=col, count=null_count, strategy=strategy)

    return result


def cast_dtypes(
    df: pd.DataFrame,
    schema: dict[str, str],
) -> pd.DataFrame:
    """Cast DataFrame columns to specified dtypes.

    Args:
        df: Input DataFrame.
        schema: Mapping of column name to dtype string, e.g. ``{"age": "int64", "flag": "bool"}``.

    Returns:
        DataFrame with columns cast to the requested dtypes.

    Raises:
        KeyError: If any column in schema is absent from the DataFrame.
        ValueError: If a cast fails due to incompatible values.
    """
    missing = [col for col in schema if col not in df.columns]
    if missing:
        raise KeyError(f"Columns not in DataFrame: {missing}")

    result = df.copy()
    for col, dtype in schema.items():
        try:
            result[col] = result[col].astype(dtype)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Cannot cast column {col!r} to {dtype!r}: {exc}") from exc
    return result


def clip_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    factor: float = 1.5,
) -> pd.DataFrame:
    """Clip outlier values to computed bounds.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to process.
        method: ``"iqr"`` (interquartile range) or ``"zscore"``.
        factor: IQR multiplier or z-score cutoff depending on method.

    Returns:
        DataFrame with outlier values clipped to the lower and upper bounds.

    Raises:
        ValueError: If method is not ``"iqr"`` or ``"zscore"``.
    """
    if method not in ("iqr", "zscore"):
        raise ValueError(f"method must be 'iqr' or 'zscore', got {method!r}")

    result = df.copy()
    for col in columns:
        if col not in result.columns:
            continue
        series: pd.Series = result[col]  # type: ignore[type-arg]
        if method == "iqr":
            q1: float = series.quantile(0.25)
            q3: float = series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - factor * iqr, q3 + factor * iqr
        else:
            mean: float = series.mean()
            std: float = series.std()
            lower, upper = mean - factor * std, mean + factor * std
        clipped: pd.Series = series.clip(lower=lower, upper=upper)  # type: ignore[type-arg]
        n_clipped = int((series != clipped).sum())
        if n_clipped:
            log.debug("clipped_outliers", column=col, count=n_clipped, method=method)
        result[col] = clipped
    return result
