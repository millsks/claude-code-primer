"""Integration test fixtures — requires a live PostgreSQL instance via DATABASE_URL."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from fastapi_project.main import app


@pytest.fixture(scope="session", autouse=True)
def require_database() -> None:
    """Skip the entire integration suite when no DATABASE_URL is set."""
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set — integration tests require a live PostgreSQL instance")


@pytest.fixture
async def client() -> AsyncClient:
    """Yield an AsyncClient wired to the FastAPI app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
