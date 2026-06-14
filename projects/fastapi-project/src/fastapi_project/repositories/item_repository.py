"""Data access for the items table."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_project.db.models import Item


class ItemRepository:
    """Async repository for Item persistence."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an active async session."""
        self._session = session

    async def get_by_id(self, item_id: int) -> Item | None:
        """Return the item with the given id, or None if not found."""
        result = await self._session.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Item]:
        """Return all items ordered by id."""
        result = await self._session.execute(select(Item).order_by(Item.id))
        return list(result.scalars().all())

    async def create(self, name: str, description: str | None) -> Item:
        """Persist a new item and return it with its generated id."""
        item = Item(name=name, description=description)
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        """Delete an item from the database."""
        await self._session.delete(item)
        await self._session.commit()
