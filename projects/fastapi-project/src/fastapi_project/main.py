"""FastAPI application factory."""

from fastapi import FastAPI

from fastapi_project.routers import health, items


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    app = FastAPI(
        title="FastAPI Project",
        version="0.1.0",
        description="REST API with SQLAlchemy 2.0 async and PostgreSQL.",
    )
    app.include_router(health.router)
    app.include_router(items.router)
    return app


app = create_app()
