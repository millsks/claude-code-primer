---
name: new-py-module
description: Scaffold a new Python module and its test counterpart in a Pixi-managed Python project, applying all conventions from CLAUDE.md — structlog logging, full type hints (3.10+ syntax), Google docstrings, no print(). Use this skill when the user says "new Python module", "add a Python module", "scaffold a module", "create a module for X", "start a new Python component", "I need a Python file for X", or asks to create any new src/<package>/<name>.py file with accompanying tests. Trigger on any request to stand up a new Python source file — even if the user just says "add a <thing> module" without mentioning tests.
argument-hint: <module-name> [--integration]
compatibility: Python 3.10+ · Pixi package manager · src/<package>/ layout · pixi.toml at project root
disable-model-invocation: false
license: MIT
metadata:
  author: Kevin Mills
  tags: python, pixi, scaffolding, structlog, type-hints, testing, google-docstrings
user-invokable: true
---

# new-py-module

Scaffold a Python module + test file pair for any Pixi-managed Python project. Every file this skill creates is immediately valid: it passes `pixi run fmt`, `pixi run lint`, `pixi run check`, and `pixi run test` before you hand control back to the user.

## Arguments

`$ARGUMENTS` is expected as: `<module-name> [--integration]`

| Argument | Required | Description |
|---|---|---|
| `<module-name>` | yes | snake_case name (e.g. `parser`, `csv_reader`) |
| `--integration` | no | also scaffold `tests/integration/test_<module>.py` |

If `$ARGUMENTS` is empty, ask the user for the module name before doing anything else.

## Step 1 — Discover the project layout

Run in parallel:

```bash
cat pixi.toml
find src -maxdepth 2 -name "__init__.py" | sort
```

From `pixi.toml`, extract the package name: it is the value of `name` under `[project]` or `[workspace]`, with hyphens converted to underscores.

Confirm `src/<package>/` exists. If it does not, stop and tell the user — this skill assumes the standard src layout.

## Step 2 — Scaffold the source module

Create `src/<package>/<module_name>.py`.

Use the **Module template** from `references/templates.md`. Adapt it:
- Replace `<module_name>` with the actual module name (snake_case)
- Replace `<ClassName>` with PascalCase of the module name (e.g. `csv_reader` → `CsvReader`)
- Set the one-line module docstring to describe what the module will do
- If the module name implies a specific domain (e.g. `parser`, `watcher`, `exporter`), name the example class/function accordingly — do not leave generic placeholder names in the final file

Keep the scaffolded surface minimal: one public class with one public method is the right default. The user will flesh it out.

## Step 3 — Scaffold unit tests

Create `tests/unit/test_<module_name>.py`.

Use the **Unit test template** from `references/templates.md`. Adapt it:
- Import from the correct package path (`from <package>.<module_name> import <ClassName>`)
- Write two tests: one for the happy-path return value, one that confirms logging behaviour (or a meaningful edge case if the class has no logging)
- Use `tmp_path` for any filesystem fixtures — never mock the filesystem

## Step 4 — Scaffold integration tests (conditional)

Only if `--integration` was in `$ARGUMENTS`: create `tests/integration/test_<module_name>.py`.

Use the **Integration test template** from `references/templates.md`. Every test must carry `@pytest.mark.integration`. Leave a `# TODO:` comment indicating what real resource (filesystem, network, DB) the tests should exercise.

## Step 5 — Validate

Run these in sequence — do not skip or reorder:

1. `pixi run fmt` — auto-format; re-stage any modified files if running inside the harness
2. `pixi run lint` — must exit 0
3. `pixi run check` — mypy strict; must exit 0
4. `pixi run test` — unit suite must pass

If any step fails, fix the generated files and re-run from step 1 of validation. Never use `# type: ignore` or `noqa` to silence errors — fix the root cause.

## Step 6 — Report

Tell the user:

- The exact file paths created
- The public name (class or function) to start building from
- Whether they need to add an export to `src/<package>/__init__.py`
- The command to run to confirm everything still passes: `pixi run test`
