"""Integration tests for the /items router — requires a live PostgreSQL instance."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_list_items_empty(client: AsyncClient) -> None:
    """GET /items returns an empty list when no items exist."""
    response = await client.get("/items/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
async def test_create_and_retrieve_item(client: AsyncClient) -> None:
    """POST /items creates an item, GET /items/{id} retrieves it."""
    created = await client.post("/items/", json={"name": "Gadget", "description": "A test gadget"})
    assert created.status_code == 201
    item_id = created.json()["id"]

    fetched = await client.get(f"/items/{item_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Gadget"


@pytest.mark.integration
async def test_get_missing_item_returns_404(client: AsyncClient) -> None:
    """GET /items/{id} returns 404 for an id that does not exist."""
    response = await client.get("/items/999999")
    assert response.status_code == 404
