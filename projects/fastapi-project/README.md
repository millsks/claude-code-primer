# fastapi-project

FastAPI REST API with SQLAlchemy 2.0 async, PostgreSQL, and Alembic migrations.

## Installation

```sh
pixi install
pixi run bootstrap
```

## Quick start

```sh
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/fastapi_project
pixi run migrate
pixi run dev
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Development

```sh
pixi run test           # unit tests (no DB required)
pixi run test-integration  # integration tests (PostgreSQL required)
pixi run ci             # full gate: fmt + lint + mypy + cov
```

Run a single test:

```sh
pixi run -- pytest tests/unit/test_item_service.py::test_create_item -v
```

## License

MIT
