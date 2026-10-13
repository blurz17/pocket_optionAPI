import asyncio
import io
import csv
import logging
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from app.config import config
from app.database import db
from app.collector.engine import engine, EngineStatus
from app.alerts.telegram import notifier

logger = logging.getLogger("web.server")
app = FastAPI(title="Pocket Option Data Harvester Dashboard")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class SessionUpdateRequest(BaseModel):
    session: str
    uid: Optional[int] = None
    is_demo: Optional[int] = None

class ConfigUpdateRequest(BaseModel):
    timeframe: int
    symbols: List[str]

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Database on startup...")
    await db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Harvester...")
    await engine.stop()
    await db.disconnect()
    await notifier.close()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/api/status")
async def get_status():
    status = engine.get_status()
    total_db = await db.get_total_candles_count()
    status["candles_total_db"] = total_db
    status["session_configured"] = bool(engine.session_token)
    status["uid"] = engine.uid
    status["is_demo"] = engine.is_demo
    return status

@app.post("/api/start")
async def start_collector():
    await engine.start()
    return {"ok": True, "status": engine.status.value}

@app.post("/api/pause")
async def pause_collector():
    await engine.pause()
    return {"ok": True, "status": engine.status.value}

@app.post("/api/resume")
async def resume_collector():
    await engine.resume()
    return {"ok": True, "status": engine.status.value}

@app.post("/api/stop")
async def stop_collector():
    await engine.stop()
    return {"ok": True, "status": engine.status.value}

@app.post("/api/session")
async def update_session(payload: SessionUpdateRequest):
    if not payload.session:
        raise HTTPException(status_code=400, detail="Session string is required")
    await engine.update_session(
        session=payload.session,
        uid=payload.uid,
        is_demo=payload.is_demo
    )
    return {"ok": True, "message": "Session updated successfully"}

@app.post("/api/config")
async def update_config(payload: ConfigUpdateRequest):
    engine.timeframe = payload.timeframe
    engine.symbols = [s.strip() for s in payload.symbols if s.strip()]
    engine.log("INFO", f"Config updated: Timeframe={engine.timeframe}s, Symbols count={len(engine.symbols)}")
    return {"ok": True, "timeframe": engine.timeframe, "symbols": engine.symbols}

@app.get("/api/candles")
async def get_recent_candles(symbol: Optional[str] = None, limit: int = 25):
    candles = await db.get_recent_candles(symbol=symbol, timeframe=engine.timeframe, limit=limit)
    return {"candles": candles}

@app.get("/api/export")
async def export_csv(symbol: Optional[str] = None, limit: int = 5000):
    candles = await db.get_recent_candles(symbol=symbol, timeframe=engine.timeframe, limit=limit)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume", "created_at"])
    for c in candles:
        writer.writerow([
            c["symbol"], c["timeframe"], c["timestamp"],
            c["open"], c["high"], c["low"], c["close"],
            c["volume"], c["created_at"]
        ])
    output.seek(0)
    filename = f"pocket_option_candles_{symbol or 'all'}_{engine.timeframe}s.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/test-telegram")
async def test_telegram_alert():
    ok = await notifier.send_message("🧪 *Test Alert:* Pocket Option Harvester Telegram integration is functioning correctly!")
    return {"ok": ok}

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    await websocket.accept()
    log_queue = asyncio.Queue(maxsize=100)
    engine.add_log_listener(log_queue)

    try:
        while True:
            # Send status update and logs
            try:
                log_entry = await asyncio.wait_for(log_queue.get(), timeout=1.0)
                await websocket.send_json({"type": "log", "data": log_entry})
            except asyncio.TimeoutError:
                # Heartbeat status update every 1 second
                await websocket.send_json({"type": "status", "data": engine.get_status()})
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        engine.remove_log_listener(log_queue)
