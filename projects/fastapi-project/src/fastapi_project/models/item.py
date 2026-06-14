"""Pydantic schemas for the item resource."""

from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    """Payload for creating a new item."""

    name: str
    description: str | None = None


class ItemUpdate(BaseModel):
    """Payload for updating an existing item (all fields optional)."""

    name: str | None = None
    description: str | None = None


class ItemResponse(BaseModel):
    """Item representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
