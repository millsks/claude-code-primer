# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.
Global rules (toolchain, coding standards, test requirements, git workflow, harness, control constraints) live in `~/.claude/CLAUDE.md` and apply here unchanged. This file covers only what is specific to this project.

---

## Project Overview

**logwatch** — a Python CLI tool that monitors log files for patterns (errors, warnings) with real-time tail mode and colored output. Mini-Project 1 from the [Claude Code Primer](../../docs/claude_code_complete_guide.md).

Tech stack: Python 3.12–3.14, `click` (CLI), `rich` (output), `pytest` + `ruff` + `mypy` (dev tooling). **Pixi manages all dependencies and tasks** — never use `pip install` directly.

---

## Commands

```bash
# First-time setup
pixi install
pixi run bootstrap        # installs pre-commit hooks

# Run the tool
pixi run watch -- /path/to/file.log
pixi run watch -- --no-tail --summary /path/to/file.log
pixi run watch -- --level error --pattern "timeout" /path/to/file.log

# Inner loop (run frequently while developing)
pixi run test             # unit tests — milliseconds
pixi run fmt              # ruff format
pixi run lint             # ruff check
pixi run check            # mypy

# Full CI gate (must exit 0 before committing)
pixi run ci               # build → cov → check → lint

# Other tasks
pixi run cov              # pytest with coverage (≥90% required)
pixi run changelog        # generate CHANGELOG.md via git-cliff
pixi run act              # run CI locally via nektos/act
```

---

## Architecture

Src layout under `src/logwatch/`:

| Module | Purpose |
|---|---|
| `watcher.py` | Core logic: `LogWatcher`, `LogEntry`, `WatcherStats` dataclasses. Level detection via `LEVEL_PATTERNS` dict — insertion order is priority (error before warning). |
| `output.py` | Rich formatting: `format_entry()` returns a styled `Text` object; `print_entry()` and `print_summary()` write to a module-level `Console`. |
| `cli.py` | Click command (`main`). `--tail/--no-tail` controls real-time mode; `--summary` scans once and prints stats; `--level` filters by severity; `--pattern` accepts multiple extra regexes. |
| `__main__.py` | Enables `python -m logwatch`. |

### Key invariants

- `watcher.tail()` first yields from `scan(last_n=N)` (with correct absolute line numbers), then enters a `readline()` poll loop after seeking to EOF. Never change this order — tests rely on the initial backfill appearing before live lines.
- `scan()` uses `splitlines()`, not `readlines()`, so trailing newlines never produce empty `LogEntry` objects.
- Lines appended via `tail()` get `line_number=-1`; only `scan()` yields entries with real line numbers.
- `LEVEL_PATTERNS` dict insertion order determines match priority — first match wins. Do not reorder the keys.
- `--summary` implies `--no-tail`; the CLI enforces this via `if tail and not summary`.

### Output styling

`LEVEL_STYLES` and `LEVEL_LABELS` in `output.py` are the single source of truth for how each severity is displayed. Any new level keyword added to `LEVEL_PATTERNS` in `watcher.py` must get a corresponding entry in both dicts.

---

## Testing

All tests live under `tests/` (flat, no `unit/`/`integration/` split for this project — the suite is small and all tests use real files via `tmp_path`).

| File | Covers |
|---|---|
| `test_watcher.py` | `LogWatcher.detect_level`, `scan()`, `tail()`, stats accumulation |
| `test_cli.py` | Click `main` command via `CliRunner` |
| `test_output.py` | `format_entry()`, `print_summary()` |

**Testing conventions for this project:**

- Use `tmp_path` (real files) — never mock the filesystem.
- CLI tests use Click's `CliRunner`, not subprocess.
- `tail()` tests use `threading.Thread` to write to the file concurrently; always join the writer thread and assert on collected output, not timing.
- Coverage gate is 90% (`pixi run cov`).

---

## CI Gate

`pixi run ci` runs: `build` → `cov` (full suite + coverage) → `check` (mypy) → `lint` (ruff). Note: this project's `ci` task does **not** include a separate `pre-commit` step in `depends-on` — pre-commit runs at the `commit-msg` stage via the installed hook.

CI matrix: Python 3.12, 3.13, 3.14-dev (3.14-dev is `continue-on-error`). See `.github/workflows/ci.yml`.
