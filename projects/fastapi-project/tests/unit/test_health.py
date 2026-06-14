"""Unit tests for the health check endpoint."""

from fastapi.testclient import TestClient

from fastapi_project.main import app


def test_health_returns_ok() -> None:
    """Health endpoint returns 200 and the expected JSON body."""
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
