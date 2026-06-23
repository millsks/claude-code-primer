# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A comprehensive guide to Claude Code mastery (`docs/claude_code_complete_guide.md`) bundled with a mono-repo of example projects that illustrate the concepts taught in the guide. The guide is the primary artifact; `projects/` is the mono-repo root.

## Root-Level Commands

The root `pixi.toml` has one task:

```sh
pixi run changelog   # regenerate CHANGELOG.md via git-cliff
```

The root environment contains only `git-cliff` and `gh`. All development tasks belong to individual projects under `projects/`.

## Layout

```text
docs/
  claude_code_complete_guide.md   # the guide — primary artifact
projects/                         # mono-repo root
  agents-work/      # pixi; Claude Agent SDK and orchestration examples (has own CLAUDE.md)
  data-wrangler/    # conda + Make (not pixi); data processing example
  django-demo/      # Django with requirements.txt (legacy toolchain)
  fastapi-project/  # pixi + FastAPI + SQLAlchemy async + PostgreSQL (has own CLAUDE.md)
  my-cli-tool/      # pixi + logwatch CLI tool
  skills-work/      # pixi + minimal module; Skills system demo
```

## Working on Projects

Each project under `projects/` is self-contained. `cd` into the project directory and use its toolchain:

- **pixi-based projects** (`agents-work`, `fastapi-project`, `my-cli-tool`, `skills-work`): use `pixi run <task>`; standard tasks from the global CLAUDE.md apply.
- **data-wrangler**: uses `conda` + `make`; run `make ci` for the full gate.
- **django-demo**: uses plain `pip` + `requirements.txt`; no pixi.

Projects with their own `CLAUDE.md` (`agents-work`, `fastapi-project`) extend these conventions — read that file first.

## Guide Authoring

`docs/claude_code_complete_guide.md` is a single-file Markdown document with a YAML front-matter block. The front-matter fields (`version`, `date`, `topics`, etc.) must be kept in sync when the guide content changes. The license is CC BY 4.0.

Do not split the guide into multiple files — it is intentionally a single portable document.

## Adding a New Project

1. Scaffold with `pixi init projects/<name>` (never write `pixi.toml` by hand).
2. Create a `README.md` in the project directory.
3. If the project has non-obvious conventions, add a `CLAUDE.md` there.
4. Each new project must follow the standard task names from the global CLAUDE.md (`fmt`, `lint`, `check`, `test`, `cov`, `ci`).
