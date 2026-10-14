# Pocket Option Data Harvester — Collector control routes
from fastapi import APIRouter, Request
from app.collector.engine import EngineStatus
from app.core.errors import CollectorAlreadyRunning, CollectorNotRunning

collector_router = APIRouter()


def _get_engine(request: Request):
    return request.app.state.engine


@collector_router.get("/status")
async def get_status(request: Request):
    """Return engine metrics plus total DB candle count."""
    engine = _get_engine(request)
    db = request.app.state.db
    status = engine.get_status()
    status["candles_total_db"] = await db.get_total_candles_count()
    status["session_configured"] = bool(engine.session_token)
    status["uid"] = engine.uid
    status["is_demo"] = engine.is_demo
    return status


@collector_router.post("/start")
async def start_collector(request: Request):
    """Start the collector engine."""
    engine = _get_engine(request)
    if engine.status in (EngineStatus.RUNNING, EngineStatus.STARTING):
        raise CollectorAlreadyRunning()
    await engine.start()
    return {"ok": True, "status": engine.status.value}


@collector_router.post("/pause")
async def pause_collector(request: Request):
    """Pause a running collector."""
    engine = _get_engine(request)
    if engine.status == EngineStatus.STOPPED:
        raise CollectorNotRunning()
    await engine.pause()
    return {"ok": True, "status": engine.status.value}


@collector_router.post("/resume")
async def resume_collector(request: Request):
    """Resume a paused collector."""
    engine = _get_engine(request)
    if engine.status == EngineStatus.STOPPED:
        raise CollectorNotRunning()
    await engine.resume()
    return {"ok": True, "status": engine.status.value}


@collector_router.post("/stop")
async def stop_collector(request: Request):
    """Stop the collector engine."""
    engine = _get_engine(request)
    await engine.stop()
    return {"ok": True, "status": engine.status.value}
