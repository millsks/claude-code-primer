# datawrangler

Data wrangling and analysis utilities for Python — cleaning, transforming, aggregating, and reading/writing tabular data.

[![CI](https://github.com/millsks/claude-code-primer/actions/workflows/ci.yml/badge.svg)](https://github.com/millsks/claude-code-primer/actions)

## Installation

```bash
conda env create -f environment.yml
conda activate data-wrangler
```

The `environment.yml` includes the package as an editable install, so the library is immediately importable after environment creation.

## Quick start

```python
import datawrangler as dw

# Load
df = dw.read_csv("data/sales.csv")

# Clean
df = dw.drop_duplicates(df)
df = dw.fill_nulls(df, strategy="median")
df = dw.clip_outliers(df, columns=["revenue"], method="iqr")

# Transform
df = dw.normalize(df, columns=["revenue", "qty"], method="minmax")
long_df = dw.reshape_wide_to_long(df, id_vars=["id"], value_vars=["q1", "q2"])

# Aggregate
summary = dw.group_summary(df, by=["region"], agg={"revenue": "sum", "qty": "mean"})
pivot = dw.pivot_summary(df, index="region", columns="product", values="revenue")

# Write
dw.write_parquet(summary, "output/summary.parquet")
```

## API

| Module | Function | Description |
|---|---|---|
| `clean` | `drop_duplicates(df, subset, keep)` | Remove duplicate rows |
| `clean` | `fill_nulls(df, strategy, fill_value, columns)` | Fill NaN by mean / median / mode / constant |
| `clean` | `cast_dtypes(df, schema)` | Cast columns to specified dtypes |
| `clean` | `clip_outliers(df, columns, method, factor)` | Clip outliers by IQR or z-score |
| `transform` | `normalize(df, columns, method)` | Min-max or z-score normalization |
| `transform` | `encode_categoricals(df, columns, method)` | One-hot or label encoding |
| `transform` | `reshape_wide_to_long(df, id_vars, value_vars, ...)` | Wide → long (melt) |
| `aggregate` | `group_summary(df, by, agg)` | GroupBy with flat column names |
| `aggregate` | `rolling_stats(df, column, window, stats)` | Rolling mean / std / min / max |
| `aggregate` | `pivot_summary(df, index, columns, values, aggfunc)` | Pivot table |
| `io` | `read_csv / write_csv` | CSV I/O |
| `io` | `read_parquet / write_parquet` | Parquet I/O (via pyarrow) |
| `io` | `read_excel` | Excel I/O (via openpyxl) |

## Development

```bash
# One-time setup
make bootstrap

# During development
make fmt        # ruff format
make lint       # ruff check
make check      # mypy
make test       # unit tests only (fast)
make test-integration  # integration tests

# Full CI gate (required before any commit)
make ci
```

## License

MIT
