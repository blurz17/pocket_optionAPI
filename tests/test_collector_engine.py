"""
test_collector_engine.py — Unit tests for CollectorEngine state machine.
Uses mock db and notifier — no real WebSocket connections.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.collector.engine import CollectorEngine, EngineStatus
from app.core.errors import CollectorAlreadyRunning


class TestEngineInitialization:

    def test_initial_status_is_stopped(self, engine):
        assert engine.status == EngineStatus.STOPPED

    def test_initial_metrics_present(self, engine):
        status = engine.get_status()
        for key in ["status", "candles_total", "ticks_total", "uptime_seconds", "active_symbols"]:
            assert key in status

    def test_uptime_zero_before_start(self, engine):
        assert engine.get_status()["uptime_seconds"] == 0

    def test_injected_db_assigned(self, engine, mock_db):
        assert engine._db is mock_db

    def test_injected_notifier_assigned(self, engine, mock_notifier):
        assert engine._notifier is mock_notifier


class TestLogListeners:

    def test_add_log_listener(self, engine):
        q = asyncio.Queue()
        engine.add_log_listener(q)
        assert q in engine._log_listeners

    def test_remove_log_listener(self, engine):
        q = asyncio.Queue()
        engine.add_log_listener(q)
        engine.remove_log_listener(q)
        assert q not in engine._log_listeners

    def test_remove_nonexistent_listener_no_error(self, engine):
        q = asyncio.Queue()
        engine.remove_log_listener(q)  # Should not raise

    async def test_log_broadcasts_to_listener(self, engine):
        q = asyncio.Queue(maxsize=10)
        engine.add_log_listener(q)
        engine.log("INFO", "Hello test")
        assert not q.empty()
        entry = q.get_nowait()
        assert entry["message"] == "Hello test"
        assert entry["level"] == "INFO"

    async def test_log_does_not_raise_on_full_queue(self, engine):
        q = asyncio.Queue(maxsize=1)
        q.put_nowait({"msg": "existing"})
        engine.add_log_listener(q)
        engine.log("INFO", "overflow")  # Should not raise


class TestEngineLifecycle:

    async def test_start_raises_if_already_running(self, engine):
        engine.status = EngineStatus.RUNNING
        with pytest.raises(CollectorAlreadyRunning):
            await engine.start()

    async def test_start_raises_if_starting(self, engine):
        engine.status = EngineStatus.STARTING
        with pytest.raises(CollectorAlreadyRunning):
            await engine.start()

    async def test_stop_when_already_stopped_is_noop(self, engine):
        """stop() on a STOPPED engine should not raise."""
        assert engine.status == EngineStatus.STOPPED
        await engine.stop()  # Should not raise

    async def test_pause_only_when_running(self, engine):
        engine.status = EngineStatus.STOPPED
        await engine.pause()
        # Should not change status since it was STOPPED
        assert engine.status == EngineStatus.STOPPED

    async def test_resume_only_when_paused(self, engine):
        engine.status = EngineStatus.STOPPED
        await engine.resume()
        assert engine.status == EngineStatus.STOPPED

    async def test_pause_when_running(self, engine):
        engine.status = EngineStatus.RUNNING
        await engine.pause()
        assert engine.status == EngineStatus.PAUSED

    async def test_resume_when_paused(self, engine):
        engine.status = EngineStatus.PAUSED
        engine._pause_event.clear()
        await engine.resume()
        assert engine.status == EngineStatus.RUNNING
        assert engine._pause_event.is_set()


class TestSessionUpdate:

    async def test_update_session_changes_token(self, engine):
        await engine.update_session(session="new-token-xyz")
        assert engine.session_token == "new-token-xyz"

    async def test_update_session_strips_whitespace(self, engine):
        await engine.update_session(session="  token-abc  ")
        assert engine.session_token == "token-abc"

    async def test_update_session_updates_uid(self, engine):
        await engine.update_session(session="tok", uid=99999)
        assert engine.uid == 99999

    async def test_update_session_updates_is_demo(self, engine):
        await engine.update_session(session="tok", is_demo=0)
        assert engine.is_demo == 0

    async def test_update_session_does_not_change_uid_if_none(self, engine):
        original_uid = engine.uid
        await engine.update_session(session="tok", uid=None)
        assert engine.uid == original_uid

    async def test_update_session_in_auth_error_triggers_start(self, engine):
        """When in AUTH_ERROR state, updating session should restart the engine."""
        engine.status = EngineStatus.AUTH_ERROR
        # Patch _run_loop to avoid real WebSocket connection
        with patch.object(engine, "_run_loop", new=AsyncMock()):
            await engine.update_session(session="fresh-token")
        # Status should have changed from AUTH_ERROR
        assert engine.status != EngineStatus.AUTH_ERROR


class TestStatusMetrics:

    def test_get_status_includes_all_keys(self, engine):
        status = engine.get_status()
        expected = [
            "status", "candles_total", "candles_per_min", "ticks_total",
            "uptime_seconds", "latency_ms", "start_time", "active_symbols",
            "db_type", "last_tick_time",
        ]
        for key in expected:
            assert key in status, f"Missing key: {key}"

    def test_get_status_reflects_symbol_count(self, engine):
        engine.symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        status = engine.get_status()
        assert status["active_symbols"] == 3
