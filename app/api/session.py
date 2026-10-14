# Pocket Option Data Harvester — Session management route
from fastapi import APIRouter, Request
from app.schemas.collector import SessionUpdateRequest

session_router = APIRouter()


@session_router.post("/session")
async def update_session(request: Request, payload: SessionUpdateRequest):
    """Update the active Pocket Option session token."""
    engine = request.app.state.engine
    await engine.update_session(
        session=payload.session,
        uid=payload.uid,
        is_demo=payload.is_demo,
    )
    return {"ok": True, "message": "Session updated successfully"}
