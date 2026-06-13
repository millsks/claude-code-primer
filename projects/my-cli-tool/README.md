# logwatch

A Python CLI tool that monitors log files for patterns (errors, warnings) with real-time tail mode and colored terminal output.

Built as Mini-Project 1 of the [Claude Code Primer](../../docs/claude_code_complete_guide.md).

## Features

- Real-time tail mode (`tail -f` style)
- Automatic log level detection: `error`, `warning`, `info`, `debug`
- Extra regex pattern filtering (`--pattern`)
- Colored output via [Rich](https://github.com/Textualize/rich)
- Summary table with counts by level

## Requirements

[Pixi](https://pixi.sh) — handles Python 3.12 and all dependencies.

## Setup

```bash
pixi install
```

## Usage

```bash
# Tail a log file in real-time (default)
pixi run watch -- /var/log/app.log

# Scan once, show all levels
pixi run watch -- --no-tail /var/log/app.log

# Errors only
pixi run watch -- --no-tail --level error /var/log/app.log

# Custom pattern filter
pixi run watch -- --no-tail --pattern "timeout|refused" /var/log/app.log

# Scan and print a summary table
pixi run watch -- --summary /var/log/app.log
```

Full options:

```
Usage: logwatch [OPTIONS] FILE

  Watch a log FILE for errors, warnings, and custom patterns.

Options:
  -p, --pattern REGEX             Extra regex pattern to match (repeatable).
  -t, --tail / -T, --no-tail      Follow new lines in real-time (like tail -f).  [default: tail]
  -n N                            Number of existing lines to show before tailing.  [default: 10]
  -l, --level [error|warning|info|debug|all]
                                  Show only lines matching this severity level.  [default: all]
  -s, --summary / -S, --no-summary
                                  Print a summary table after scanning (implies --no-tail).
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```

## Development

```bash
pixi run test       # run tests
pixi run cov        # tests with coverage
pixi run lint       # ruff check
pixi run fmt        # ruff format
pixi run check      # mypy type-check
```
