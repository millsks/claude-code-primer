"""Unit tests for ItemService — repository is mocked, no DB required."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from fastapi_project.db.models import Item
from fastapi_project.models.item import ItemCreate, ItemResponse
from fastapi_project.services.item_service import ItemService


@pytest.fixture
def mock_repo() -> MagicMock:
    """Return a MagicMock standing in for ItemRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_repo: MagicMock) -> ItemService:
    """Return an ItemService backed by the mock repository."""
    return ItemService(mock_repo)


async def test_get_item_returns_response(service: ItemService, mock_repo: MagicMock) -> None:
    """get_item maps a found ORM item to ItemResponse."""
    mock_repo.get_by_id = AsyncMock(return_value=Item(id=1, name="Widget", description="A widget"))
    result = await service.get_item(1)
    assert result == ItemResponse(id=1, name="Widget", description="A widget")
    mock_repo.get_by_id.assert_called_once_with(1)


async def test_get_item_returns_none_when_missing(service: ItemService, mock_repo: MagicMock) -> None:
    """get_item returns None when the repository finds nothing."""
    mock_repo.get_by_id = AsyncMock(return_value=None)
    result = await service.get_item(99)
    assert result is None


async def test_list_items_maps_all_rows(service: ItemService, mock_repo: MagicMock) -> None:
    """list_items converts every ORM row to an ItemResponse."""
    mock_repo.get_all = AsyncMock(
        return_value=[Item(id=1, name="A", description=None), Item(id=2, name="B", description="desc")]
    )
    results = await service.list_items()
    assert len(results) == 2
    assert results[0].name == "A"
    assert results[1].description == "desc"


async def test_create_item_delegates_to_repo(service: ItemService, mock_repo: MagicMock) -> None:
    """create_item calls the repository with unpacked fields and returns the result."""
    mock_repo.create = AsyncMock(return_value=Item(id=7, name="New", description=None))
    result = await service.create_item(ItemCreate(name="New"))
    assert result == ItemResponse(id=7, name="New", description=None)
    mock_repo.create.assert_called_once_with(name="New", description=None)
