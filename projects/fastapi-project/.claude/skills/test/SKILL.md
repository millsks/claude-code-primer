---
name: test
description: Run the full testing workflow for fastapi-project — unit tests, integration tests, coverage report, and per-file coverage analysis flagging anything below 80%. Use this skill when the user says "run tests", "check coverage", "test everything", "show me coverage", "what's covered", "run the full test suite", or any request to validate the test suite beyond a quick unit run.
argument-hint: [--unit-only] [--integration-only] [--threshold <pct>]
compatibility: fastapi-project · pytest-asyncio · pixi at project root · PostgreSQL for integration tests
disable-model-invocation: false
license: MIT
metadata:
  author: Kevin Mills
  tags: testing, pytest, coverage, fastapi, asyncio, integration
user-invokable: true
---

# test

Run the complete test suite for fastapi-project, then surface any source files whose line coverage falls below the project threshold (80% by default).

## Arguments

`$ARGUMENTS` is expected as: `[--unit-only] [--integration-only] [--threshold <pct>]`

| Argument | Required | Description |
|---|---|---|
| `--unit-only` | no | Skip integration tests (no PostgreSQL required) |
| `--integration-only` | no | Skip unit tests; run integration suite only |
| `--threshold <pct>` | no | Override the coverage floor; defaults to `80` |

`--unit-only` and `--integration-only` are mutually exclusive. If both are given, stop and ask the user which they intended.

## Step 1 — Confirm prerequisites

If running integration tests (i.e. `--unit-only` was NOT given), verify a PostgreSQL instance is reachable:

```bash
python3 -c "
import asyncio, os, asyncpg
async def check():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    await conn.close()
asyncio.run(check())
"
```

If this fails, tell the user that `DATABASE_URL` must point to a running PostgreSQL instance before integration tests can run, then stop unless `--unit-only` was given.

## Step 2 — Run unit tests

Always run unit tests unless `--integration-only` was given.

```bash
pixi run -- pytest tests/unit/ -v --tb=short 2>&1 | tee /tmp/unit-results.txt
```

If the unit suite fails, report the failing tests and stop — do not proceed to integration tests or coverage collection while unit tests are red.

## Step 3 — Run integration tests

Skip this step if `--unit-only` was given.

```bash
pixi run -- pytest tests/integration/ -v --tb=short -m integration 2>&1 | tee /tmp/integration-results.txt
```

If the integration suite fails, report the failing tests. Still proceed to Step 4 to collect coverage for the passing tests, but clearly mark the run as failed.

## Step 4 — Generate coverage report

Run the full suite a second time with coverage instrumentation to produce both a terminal summary and a machine-readable JSON report:

```bash
pixi run -- pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=json:/tmp/coverage.json \
  --no-header \
  -q \
  2>&1 | tee /tmp/coverage-summary.txt
```

If `--unit-only` was given, replace `tests/` with `tests/unit/` above.
If `--integration-only` was given, replace `tests/` with `tests/integration/` above.

## Step 5 — Flag files below the coverage threshold

Parse `/tmp/coverage.json` to identify source files whose line coverage is below `$THRESHOLD` (default `80`):

```bash
python3 - <<'EOF'
import json, sys

threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0
with open("/tmp/coverage.json") as f:
    data = json.load(f)

under = []
for path, info in data["files"].items():
    pct = info["summary"]["percent_covered"]
    if pct < threshold:
        missing = info["missing_lines"]
        under.append((pct, path, missing))

if not under:
    print(f"All files meet the {threshold:.0f}% threshold.")
    sys.exit(0)

under.sort()
print(f"Files below {threshold:.0f}% coverage ({len(under)} file(s)):\n")
for pct, path, missing in under:
    lines = ", ".join(str(ln) for ln in missing[:10])
    suffix = f" … (+{len(missing)-10} more)" if len(missing) > 10 else ""
    print(f"  {pct:5.1f}%  {path}")
    print(f"         missing lines: {lines}{suffix}")
sys.exit(1)
EOF
python3 /dev/stdin "$THRESHOLD"
```

Capture the exit code. A non-zero exit means at least one file is under threshold.

## Step 6 — Report

Present a summary with four sections:

**Unit tests** — pass/fail count and any failures by name.

**Integration tests** — pass/fail count and any failures by name (or "skipped" if `--unit-only`).

**Overall coverage** — the aggregate percentage from `/tmp/coverage-summary.txt`.

**Files below threshold** — the full output from Step 5, or "All files meet the 80% threshold." if none.

End with a clear verdict line:

- `PASS` — both suites green and all files at or above threshold
- `FAIL (tests)` — one or more tests failed
- `FAIL (coverage)` — tests passed but files are below threshold
- `FAIL (tests + coverage)` — both conditions
