# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A FastAPI REST API. The global CLAUDE.md governs toolchain (Pixi, ruff, mypy, pytest), commit format, CI gate, and test requirements — read it first. Project-specific overrides are listed below.

**Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Alembic (migrations), pytest-asyncio.

## Off-limits

- `alembic/versions/` — never edit migration files by hand; always generate with `alembic revision --autogenerate`
- `.github/workflows/` — CI pipeline is managed centrally; do not modify without explicit instruction

## Commands

```sh
pixi run dev          # start uvicorn with hot-reload (localhost:8000)
pixi run test         # unit tests only (no I/O)
pixi run ci           # full gate: pre-commit → build → check → lint → cov
pixi run migrate      # alembic upgrade head
pixi run migration m="<msg>"   # generate a new migration
```

Run a single test file or test by node ID:

```sh
pixi run -- pytest tests/unit/test_items.py -v
pixi run -- pytest tests/unit/test_items.py::test_create_item -v
```

Relevant `pixi.toml` tasks:

```toml
[tasks]
dev = "uvicorn fastapi_project.main:app --reload --port 8000"
migrate = "alembic upgrade head"
migration = "alembic revision --autogenerate -m"
cov = "pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80"
```

Coverage threshold for this project is **80%** (overrides the global 90% default).

## Coding Standards

These apply in addition to the global CLAUDE.md rules:

- All public functions and methods require full type hints on every parameter and the return type.
- All public functions, methods, and classes require Google-style docstrings.
- All async route handlers and service methods must be `async def`; use `asyncio`-compatible drivers throughout (e.g., `asyncpg`, `sqlalchemy.ext.asyncio`).
- SQLAlchemy ORM models live in `db/models.py`; Pydantic schemas live in `models/` — never mix the two.

## Testing

- Use `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`.
- Unit tests mock the repository layer; no real DB required.
- Integration tests use `AsyncClient` from `httpx` (not `TestClient`) against a real PostgreSQL instance.
- Each integration test that writes data must use a transactional fixture that rolls back on teardown.
- Coverage gate: **80%** (set via `pixi run cov`; see task definition above).

## Architecture

```text
src/
  fastapi_project/
    main.py           # app factory: creates FastAPI(), registers routers, adds middleware
    dependencies.py   # shared Depends() callables (auth, db session, pagination)
    routers/          # one file per resource (items.py, users.py, health.py)
    models/           # Pydantic request/response schemas only
    services/         # business logic — routers call services, services call repositories
    repositories/     # data access; all async SQLAlchemy queries live here, nowhere else
    db/
      session.py      # async engine, AsyncSession factory
      models.py       # SQLAlchemy ORM mapped classes
alembic/
  env.py
  versions/           # OFF-LIMITS — generated only
tests/
  unit/               # test services with mocked repositories
  integration/        # test routers end-to-end with AsyncClient and real PostgreSQL
```

### Key conventions

**Request/response separation.** Define distinct Pydantic models for input (`ItemCreate`), output (`ItemResponse`), and internal state — never reuse the same model for all three.

**Services own business logic.** Routers are thin: validate input, call a service, return a response. No SQL or business rules in router handlers.

**Repositories own data access.** Services call repository methods; they never import SQLAlchemy directly. This boundary keeps services unit-testable without a database.

**Dependency injection for shared state.** Database sessions, the current user, and pagination parameters come in via `Depends()`. No module-level globals for request-scoped state.

**Health check.** `/health` router returns `{"status": "ok"}` with no auth required. Always the first router registered.
