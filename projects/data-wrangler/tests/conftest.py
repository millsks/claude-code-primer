"""Shared fixtures for unit and integration tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture()
def numeric_df() -> pd.DataFrame:
    """Simple numeric DataFrame with known values."""
    return pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0], "b": [10.0, 20.0, 30.0, 40.0, 50.0]})


@pytest.fixture()
def df_with_nulls() -> pd.DataFrame:
    """DataFrame containing NaN values in every column."""
    return pd.DataFrame({"x": [1.0, np.nan, 3.0, np.nan, 5.0], "y": [np.nan, 2.0, np.nan, 4.0, 5.0]})


@pytest.fixture()
def categorical_df() -> pd.DataFrame:
    """DataFrame with a mix of numeric and categorical columns."""
    return pd.DataFrame({"id": [1, 2, 3, 4], "color": ["red", "blue", "red", "green"], "size": ["S", "M", "L", "M"]})


@pytest.fixture()
def sales_df() -> pd.DataFrame:
    """Sales-style DataFrame suitable for aggregation tests."""
    return pd.DataFrame(
        {
            "region": ["North", "North", "South", "South", "East"],
            "product": ["A", "B", "A", "B", "A"],
            "sales": [100.0, 200.0, 150.0, 250.0, 120.0],
            "qty": [10, 20, 15, 25, 12],
        }
    )
