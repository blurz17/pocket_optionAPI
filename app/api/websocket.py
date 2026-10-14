# Pocket Option Data Harvester — WebSocket log streaming route
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


@ws_router.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """
    Streams real-time log entries and periodic status heartbeats to the dashboard.

    Protocol:
        {"type": "log",    "data": {"time": ..., "level": ..., "message": ...}}
        {"type": "status", "data": {...engine metrics...}}
    """
    await websocket.accept()

    engine = websocket.app.state.engine
    db = websocket.app.state.db
    log_queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    engine.add_log_listener(log_queue)

    cached_db_total = 0
    try:
        cached_db_total = await db.get_total_candles_count()
    except Exception:
        pass

    last_db_check = 0.0

    try:
        while True:
            try:
                log_entry = await asyncio.wait_for(log_queue.get(), timeout=1.0)
                await websocket.send_json({"type": "log", "data": log_entry})
            except asyncio.TimeoutError:
                # Heartbeat: send current status snapshot with live DB count every ~1 second
                status = engine.get_status()
                loop_time = asyncio.get_running_loop().time()
                if loop_time - last_db_check > 3.0:
                    try:
                        cached_db_total = await db.get_total_candles_count()
                        last_db_check = loop_time
                    except Exception:
                        pass
                status["candles_total_db"] = cached_db_total
                await websocket.send_json({"type": "status", "data": status})
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        engine.remove_log_listener(log_queue)

