# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**logwatch** — a Python CLI tool that monitors log files for patterns (errors, warnings) with real-time tail mode and colored output. Mini-Project 1 from the [Claude Code Primer](../../docs/claude_code_complete_guide.md).

Tech stack: Python 3.12, `click` (CLI), `rich` (output), `pytest` + `ruff` + `mypy` (dev tooling). **Pixi manages all dependencies and tasks** — do not use pip directly.

## Commands

```bash
# Install environment (first time or after pixi.toml changes)
pixi install

# Run the tool
pixi run watch -- /path/to/file.log
pixi run watch -- --no-tail --summary /path/to/file.log

# Tests
pixi run test                  # all tests
pixi run test -- -k "TestScan" # single class or test
pixi run cov                   # with coverage report

# Code quality
pixi run lint                  # ruff check
pixi run fmt                   # ruff format
pixi run check                 # mypy type-check
```

## Architecture

Src layout under `src/logwatch/`:

- `watcher.py` — core logic: `LogWatcher` scans files and tails them; `LogEntry` and `WatcherStats` are plain dataclasses. Level detection via regex (`LEVEL_PATTERNS` dict — insertion order determines priority).
- `output.py` — Rich formatting: `format_entry()` returns a styled `Text` object; `print_summary()` renders a `Table`. Module-level `console = Console()`.
- `cli.py` — Click command (`main`). `--tail/--no-tail` controls real-time mode; `--summary` scans once and prints stats; `--level` filters by severity; `--pattern` accepts multiple extra regexes.
- `__main__.py` — enables `python -m logwatch`.

`watcher.tail()` first yields from `scan(last_n=N)` (with correct absolute line numbers), then enters a `readline()` poll loop seeking to EOF. `scan()` uses `splitlines()` so trailing newlines don't produce empty entries.

Tests use `tmp_path` (real files, no mocks). CLI tests use Click's `CliRunner`.
