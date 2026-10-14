"""
conftest.py — Shared fixtures for the entire test suite.
All external dependencies (db, notifier, engine) are mocked so tests
run without any infrastructure (no database, no Telegram, no WebSocket).
"""
import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator

import pytest

# ── Ensure the project root is importable ────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Set env vars BEFORE anything imports config ───────────────────────────────
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("USE_SQLITE_FALLBACK", "true")
os.environ.setdefault("SQLITE_DB_PATH", ":memory:")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "")
os.environ.setdefault("TELEGRAM_CHAT_ID", "")
os.environ.setdefault("TELEGRAM_ENABLED", "false")
os.environ.setdefault("PO_SESSION", "test-session-token")
os.environ.setdefault("PO_UID", "12345")
os.environ.setdefault("PO_IS_DEMO", "1")
os.environ.setdefault("DEFAULT_TIMEFRAME", "60")
os.environ.setdefault("DEFAULT_SYMBOLS", "EURUSD_otc,GBPUSD_otc")


# ── Mock DB ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """AsyncMock satisfying DatabaseProtocol."""
    db = AsyncMock()
    db.connect = AsyncMock()
    db.disconnect = AsyncMock()
    db.save_candles = AsyncMock(return_value=0)
    db.get_recent_candles = AsyncMock(return_value=[])
    db.get_total_candles_count = AsyncMock(return_value=0)
    db.get_symbols_summary = AsyncMock(return_value=[])
    return db


# ── Mock Notifier ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_notifier():
    """AsyncMock TelegramNotifier with no-op methods."""
    notifier = AsyncMock()
    notifier.send_message = AsyncMock(return_value=True)
    notifier.close = AsyncMock()
    notifier.enabled = False
    notifier.notify_background = MagicMock()  # sync method
    return notifier


# ── CollectorEngine ───────────────────────────────────────────────────────────

@pytest.fixture
def engine(mock_db, mock_notifier):
    """Real CollectorEngine with mocked db and notifier."""
    from app.collector.engine import CollectorEngine
    return CollectorEngine(db=mock_db, notifier=mock_notifier)


# ── FastAPI Test Client ───────────────────────────────────────────────────────

from contextlib import asynccontextmanager

@asynccontextmanager
async def _noop_lifespan(app):
    yield


@pytest.fixture
def app_with_mocks(mock_db, mock_notifier, engine):
    """FastAPI app with all state injected as mocks (no lifespan runs)."""
    from app.main import app
    app.router.lifespan_context = _noop_lifespan
    app.state.db = mock_db
    app.state.notifier = mock_notifier
    app.state.engine = engine
    return app



@pytest.fixture
def api_client(app_with_mocks):
    """httpx AsyncClient connected to the mocked FastAPI app."""
    from httpx import AsyncClient, ASGITransport
    async def _make():
        transport = ASGITransport(app=app_with_mocks)
        return AsyncClient(transport=transport, base_url="http://testserver")
    return _make


# ── In-memory SQLite for integration tests ────────────────────────────────────

@pytest.fixture
async def sqlite_db(tmp_path):
    """Real SQLiteManager backed by a temp file for integration tests."""
    from app.database.sqlite import SQLiteManager
    db_path = str(tmp_path / "test_candles.db")
    db = SQLiteManager(db_path)
    await db.connect()
    yield db
    await db.disconnect()


# ── Sample candle data ────────────────────────────────────────────────────────

@pytest.fixture
def sample_candles():
    """A list of valid closed candle dicts."""
    return [
        {"time": 1700000000, "open": 1.1000, "high": 1.1050, "low": 1.0980, "close": 1.1020, "volume": 10.0},
        {"time": 1700000060, "open": 1.1020, "high": 1.1080, "low": 1.1010, "close": 1.1060, "volume": 12.0},
        {"time": 1700000120, "open": 1.1060, "high": 1.1090, "low": 1.1040, "close": 1.1070, "volume": 8.0},
    ]
