"""Integration test fixtures."""

import pandas as pd
import pytest


@pytest.fixture()
def wide_sales_csv(tmp_path: pytest.TempPathFactory) -> str:
    """Write a realistic wide-format CSV to a temp file and return its path."""
    df = pd.DataFrame(
        {
            "region": ["North", "South", "East", "West"] * 5,
            "product": ["A", "B", "C", "D"] * 5,
            "q1": [100, 200, 150, 80, 110, 210, 160, 90, 120, 220, 170, 100, 130, 230, 180, 110, 140, 240, 190, 120],
            "q2": [120, 220, 170, 90, 130, 230, 180, 100, 140, 240, 190, 110, 150, 250, 200, 120, 160, 260, 210, 130],
        }
    )
    p = tmp_path / "sales.csv"  # type: ignore[operator]
    df.to_csv(p, index=False)  # type: ignore[arg-type]
    return str(p)
