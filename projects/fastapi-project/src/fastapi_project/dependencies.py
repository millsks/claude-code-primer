"""Shared FastAPI dependency callables."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_project.db.session import AsyncSessionLocal
from fastapi_project.repositories.item_repository import ItemRepository
from fastapi_project.services.item_service import ItemService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it when the request completes."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_item_repository(
    session: AsyncSession = Depends(get_db),
) -> ItemRepository:
    """Provide an ItemRepository bound to the current request's session."""
    return ItemRepository(session)


async def get_item_service(
    repo: ItemRepository = Depends(get_item_repository),
) -> ItemService:
    """Provide an ItemService backed by the current request's repository."""
    return ItemService(repo)
