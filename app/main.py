# Pocket Option Data Harvester — Application Entry Point
"""
Object wiring order (linear, no circular dependency):
    1. db        — needs only config
    2. notifier  — needs only config
    3. engine    — needs db + notifier
    4. Store all three on app.state so routes access via request.app.state.*
    5. Start engine background task
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.database import get_database
from app.alerts.telegram import TelegramNotifier
from app.collector.engine import CollectorEngine
from app.core.errors import register_error_handlers

from app.api.collector import collector_router
from app.api.session import session_router
from app.api.config import config_router
from app.api.candles import candles_router
from app.api.alerts import alerts_router
from app.api.websocket import ws_router
from app.api.dashboard import dashboard_router, mount_static

logger = logging.getLogger("app.main")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Initializing application...")

    # 1. Database
    db = get_database()
    try:
        await db.connect()
    except Exception as e:
        logger.warning(f"Database connection failed ({e}). Falling back to local SQLite...")
        from app.database.sqlite import SQLiteManager
        db = SQLiteManager(config.SQLITE_DB_PATH)
        await db.connect()
    app.state.db = db


    # 2. Notifier
    notifier = TelegramNotifier()
    app.state.notifier = notifier

    # 3. Engine (receives injected db + notifier)
    engine = CollectorEngine(db=db, notifier=notifier)
    app.state.engine = engine

    logger.info("Application startup complete.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down application...")
    await engine.stop()
    await db.disconnect()
    await notifier.close()
    logger.info("Application shutdown complete.")


# ── App Factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Pocket Option Data Harvester",
    description="Real-time market data collection from Pocket Option WebSocket API.",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error Handlers ────────────────────────────────────────────────────────────

register_error_handlers(app)

# ── Static Files ──────────────────────────────────────────────────────────────

mount_static(app)

# ── Routers ───────────────────────────────────────────────────────────────────

from fastapi import APIRouter

api = APIRouter(prefix="/api")
api.include_router(collector_router, tags=["collector"])
api.include_router(session_router, tags=["session"])
api.include_router(config_router, tags=["config"])
api.include_router(candles_router, tags=["candles"])
api.include_router(alerts_router, tags=["alerts"])

app.include_router(api)
app.include_router(ws_router)
app.include_router(dashboard_router)


# ── Health Check ─────────────────────────────────────────────────────────────

@app.api_route("/healthz", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "healthy"}
