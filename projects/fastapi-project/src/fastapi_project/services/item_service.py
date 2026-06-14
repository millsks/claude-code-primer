"""Business logic for the item resource."""

from fastapi_project.models.item import ItemCreate, ItemResponse
from fastapi_project.repositories.item_repository import ItemRepository


class ItemService:
    """Orchestrates item operations, delegating persistence to ItemRepository."""

    def __init__(self, repository: ItemRepository) -> None:
        """Initialize with an item repository."""
        self._repo = repository

    async def get_item(self, item_id: int) -> ItemResponse | None:
        """Return the item with the given id, or None if it does not exist."""
        item = await self._repo.get_by_id(item_id)
        if item is None:
            return None
        return ItemResponse.model_validate(item)

    async def list_items(self) -> list[ItemResponse]:
        """Return all items."""
        items = await self._repo.get_all()
        return [ItemResponse.model_validate(i) for i in items]

    async def create_item(self, data: ItemCreate) -> ItemResponse:
        """Create a new item and return it."""
        item = await self._repo.create(name=data.name, description=data.description)
        return ItemResponse.model_validate(item)
