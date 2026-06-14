"""Unit tests for the /items router — service is overridden via dependency injection."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from fastapi_project.dependencies import get_item_service
from fastapi_project.main import app
from fastapi_project.models.item import ItemResponse


@pytest.fixture
def mock_service() -> MagicMock:
    """Return a MagicMock that stands in for ItemService."""
    return MagicMock()


@pytest.fixture
def client(mock_service: MagicMock) -> Generator[TestClient, None, None]:
    """Yield a TestClient with get_item_service overridden to return mock_service."""
    app.dependency_overrides[get_item_service] = lambda: mock_service
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


def test_list_items_returns_all(client: TestClient, mock_service: MagicMock) -> None:
    """GET /items/ returns the list produced by the service."""
    mock_service.list_items = AsyncMock(return_value=[ItemResponse(id=1, name="A"), ItemResponse(id=2, name="B")])
    response = client.get("/items/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_item_found(client: TestClient, mock_service: MagicMock) -> None:
    """GET /items/{id} returns 200 and the item when found."""
    mock_service.get_item = AsyncMock(return_value=ItemResponse(id=1, name="Widget"))
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_not_found(client: TestClient, mock_service: MagicMock) -> None:
    """GET /items/{id} returns 404 when the service returns None."""
    mock_service.get_item = AsyncMock(return_value=None)
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item(client: TestClient, mock_service: MagicMock) -> None:
    """POST /items/ returns 201 and the created item."""
    mock_service.create_item = AsyncMock(return_value=ItemResponse(id=5, name="Gadget"))
    response = client.post("/items/", json={"name": "Gadget"})
    assert response.status_code == 201
    assert response.json()["id"] == 5
