# Pocket Option Data Harvester — Config update route
from fastapi import APIRouter, Request
from app.schemas.collector import ConfigUpdateRequest

config_router = APIRouter()


@config_router.post("/config")
async def update_config(request: Request, payload: ConfigUpdateRequest):
    """Update timeframe and symbol list for the running collector."""
    engine = request.app.state.engine
    await engine.update_config(timeframe=payload.timeframe, symbols=payload.symbols)
    return {"ok": True, "timeframe": engine.timeframe, "symbols": engine.symbols}
