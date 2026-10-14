"""
test_config.py — Tests for app.config.Config loading.
"""
import os
import pytest


def test_default_timeframe():
    from app.config import config
    assert config.DEFAULT_TIMEFRAME == 60


def test_default_symbols_parsed():
    from app.config import config
    assert isinstance(config.DEFAULT_SYMBOLS, list)
    assert len(config.DEFAULT_SYMBOLS) >= 1


def test_sqlite_fallback_enabled():
    """conftest sets USE_SQLITE_FALLBACK=true so db should be SQLite."""
    from app.config import config
    assert config.USE_SQLITE_FALLBACK is True


def test_telegram_disabled_in_tests():
    """conftest disables Telegram so no real HTTP calls happen."""
    from app.config import config
    assert config.TELEGRAM_ENABLED is False


def test_demo_ws_url_format():
    from app.config import config
    assert config.DEMO_WS_URL.startswith("wss://")


def test_real_ws_url_format():
    from app.config import config
    assert config.REAL_WS_URL.startswith("wss://")


def test_get_database_returns_sqlite_when_no_url():
    from app.database import get_database
    from app.database.sqlite import SQLiteManager
    db = get_database()
    assert isinstance(db, SQLiteManager)
