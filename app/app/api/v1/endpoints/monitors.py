"""
Monitors CRUD endpoints — placeholder.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_monitors():
    """List all configured API monitors."""
    # TODO: implement
    return {"monitors": []}


@router.post("/")
async def create_monitor():
    """Create a new API monitor."""
    # TODO: implement
    return {"message": "created"}


@router.get("/{monitor_id}")
async def get_monitor(monitor_id: int):
    """Get a specific API monitor by ID."""
    # TODO: implement
    return {"monitor_id": monitor_id}


@router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: int):
    """Delete a specific API monitor."""
    # TODO: implement
    return {"message": "deleted"}
