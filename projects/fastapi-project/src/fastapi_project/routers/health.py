"""Health check endpoint — no auth, no DB dependency."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return service liveness status."""
    return {"status": "ok"}
