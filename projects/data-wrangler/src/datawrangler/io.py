"""I/O utilities for reading and writing tabular data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import structlog

log = structlog.get_logger()

_PathLike = str | Path


def read_csv(path: _PathLike, **kwargs: Any) -> pd.DataFrame:
    """Read a CSV file into a DataFrame.

    Args:
        path: Path to the CSV file.
        **kwargs: Forwarded to :func:`pandas.read_csv`.

    Returns:
        Loaded DataFrame.
    """
    p = Path(path)
    log.info("reading_csv", path=str(p))
    df: pd.DataFrame = pd.read_csv(p, **kwargs)
    log.info("read_csv_done", rows=len(df), columns=len(df.columns))
    return df


def read_parquet(path: _PathLike, columns: list[str] | None = None) -> pd.DataFrame:
    """Read a Parquet file, optionally projecting a subset of columns.

    Args:
        path: Path to the Parquet file.
        columns: Columns to read. Reads all columns when None.

    Returns:
        Loaded DataFrame.
    """
    p = Path(path)
    log.info("reading_parquet", path=str(p))
    df: pd.DataFrame = pd.read_parquet(p, columns=columns)
    log.info("read_parquet_done", rows=len(df), columns=len(df.columns))
    return df


def read_excel(path: _PathLike, sheet_name: str | int = 0, **kwargs: Any) -> pd.DataFrame:
    """Read an Excel workbook sheet into a DataFrame.

    Args:
        path: Path to the ``.xlsx`` (or ``.xls``) file.
        sheet_name: Sheet name or 0-based index. Defaults to the first sheet.
        **kwargs: Forwarded to :func:`pandas.read_excel`.

    Returns:
        Loaded DataFrame.
    """
    p = Path(path)
    log.info("reading_excel", path=str(p), sheet=sheet_name)
    df: pd.DataFrame = pd.read_excel(p, sheet_name=sheet_name, **kwargs)
    log.info("read_excel_done", rows=len(df), columns=len(df.columns))
    return df


def write_csv(df: pd.DataFrame, path: _PathLike, index: bool = False, **kwargs: Any) -> None:
    """Write a DataFrame to a CSV file.

    Args:
        df: DataFrame to write.
        path: Destination path.
        index: Whether to write the row index. Defaults to ``False``.
        **kwargs: Forwarded to :meth:`pandas.DataFrame.to_csv`.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=index, **kwargs)
    log.info("wrote_csv", path=str(p), rows=len(df))


def write_parquet(df: pd.DataFrame, path: _PathLike, compression: str = "snappy") -> None:
    """Write a DataFrame to a Parquet file.

    Args:
        df: DataFrame to write.
        path: Destination path.
        compression: Parquet compression codec. Defaults to ``"snappy"``.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, compression=compression, index=False)
    log.info("wrote_parquet", path=str(p), rows=len(df))
