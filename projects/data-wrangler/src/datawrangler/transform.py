"""Data transformation utilities."""

from __future__ import annotations

import pandas as pd
import structlog

log = structlog.get_logger()


def normalize(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "minmax",
) -> pd.DataFrame:
    """Normalize numeric columns to a common scale.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to normalize.
        method: ``"minmax"`` scales to [0, 1]; ``"zscore"`` standardizes to mean=0, std=1.

    Returns:
        DataFrame with the requested columns normalized. Columns with zero range or
        zero std are left unchanged with a warning logged.

    Raises:
        ValueError: If method is not ``"minmax"`` or ``"zscore"``.
    """
    if method not in ("minmax", "zscore"):
        raise ValueError(f"method must be 'minmax' or 'zscore', got {method!r}")

    result = df.copy()
    for col in columns:
        if col not in result.columns:
            continue
        series: pd.Series = result[col]  # type: ignore[type-arg]
        if method == "minmax":
            col_min: float = series.min()
            col_max: float = series.max()
            col_range = col_max - col_min
            if col_range == 0:
                log.warning("normalize_skipped_zero_range", column=col)
                continue
            result[col] = (series - col_min) / col_range
        else:
            mean: float = series.mean()
            std: float = series.std()
            if std == 0:
                log.warning("normalize_skipped_zero_std", column=col)
                continue
            result[col] = (series - mean) / std
    return result


def encode_categoricals(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "onehot",
) -> pd.DataFrame:
    """Encode categorical columns as numeric representations.

    Args:
        df: Input DataFrame.
        columns: Categorical columns to encode.
        method: ``"onehot"`` creates binary indicator columns (drops the original);
            ``"label"`` replaces each category with an integer code.

    Returns:
        DataFrame with categorical columns encoded. For one-hot encoding the original
        column is dropped and replaced by ``<col>_<category>`` indicator columns.

    Raises:
        ValueError: If method is not ``"onehot"`` or ``"label"``.
    """
    if method not in ("onehot", "label"):
        raise ValueError(f"method must be 'onehot' or 'label', got {method!r}")

    result = df.copy()
    for col in columns:
        if col not in result.columns:
            continue
        if method == "onehot":
            dummies = pd.get_dummies(result[col], prefix=col)
            result = pd.concat([result.drop(columns=[col]), dummies], axis=1)
        else:
            result[col] = result[col].astype("category").cat.codes
    return result


def reshape_wide_to_long(
    df: pd.DataFrame,
    id_vars: list[str],
    value_vars: list[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> pd.DataFrame:
    """Reshape a DataFrame from wide format to long format.

    Args:
        df: Input DataFrame in wide format.
        id_vars: Columns to use as identifier variables (kept as-is).
        value_vars: Columns to unpivot into rows.
        var_name: Name of the column that will hold the original column names.
        value_name: Name of the column that will hold the corresponding values.

    Returns:
        DataFrame in long format with one row per (id, variable) combination.
    """
    return df.melt(id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name)
