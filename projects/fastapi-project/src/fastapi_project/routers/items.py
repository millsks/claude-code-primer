"""Item resource router."""

from fastapi import APIRouter, Depends, HTTPException

from fastapi_project.dependencies import get_item_service
from fastapi_project.models.item import ItemCreate, ItemResponse
from fastapi_project.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    service: ItemService = Depends(get_item_service),
) -> list[ItemResponse]:
    """Return all items."""
    return await service.list_items()


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    """Return a single item by id, or 404 if not found."""
    item = await service.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    data: ItemCreate,
    service: ItemService = Depends(get_item_service),
) -> ItemResponse:
    """Create and return a new item."""
    return await service.create_item(data)
