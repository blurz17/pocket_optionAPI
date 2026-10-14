"""
test_api_collector.py — Route integration tests for collector control endpoints.
Uses mocked engine via app.state — no real WebSocket connections.
"""
import pytest
from app.collector.engine import EngineStatus


class TestGetStatus:

    async def test_status_returns_200(self, api_client, engine, mock_db):
        mock_db.get_total_candles_count.return_value = 42
        async with (await api_client()) as client:
            resp = await client.get("/api/status")
        assert resp.status_code == 200

    async def test_status_includes_candles_total_db(self, api_client, engine, mock_db):
        mock_db.get_total_candles_count.return_value = 99
        async with (await api_client()) as client:
            resp = await client.get("/api/status")
        data = resp.json()
        assert data["candles_total_db"] == 99

    async def test_status_includes_session_configured(self, api_client, engine):
        engine.session_token = "active-token"
        async with (await api_client()) as client:
            resp = await client.get("/api/status")
        assert resp.json()["session_configured"] is True

    async def test_status_session_not_configured_when_empty(self, api_client, engine):
        engine.session_token = ""
        async with (await api_client()) as client:
            resp = await client.get("/api/status")
        assert resp.json()["session_configured"] is False


class TestStartCollector:

    async def test_start_stopped_engine_returns_ok(self, api_client, engine):
        """Patching _run_loop to avoid real WebSocket."""
        from unittest.mock import AsyncMock, patch
        with patch.object(engine, "_run_loop", new=AsyncMock()):
            async with (await api_client()) as client:
                resp = await client.post("/api/start")
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    async def test_start_already_running_returns_409(self, api_client, engine):
        engine.status = EngineStatus.RUNNING
        async with (await api_client()) as client:
            resp = await client.post("/api/start")
        assert resp.status_code == 409

    async def test_start_already_starting_returns_409(self, api_client, engine):
        engine.status = EngineStatus.STARTING
        async with (await api_client()) as client:
            resp = await client.post("/api/start")
        assert resp.status_code == 409


class TestPauseCollector:

    async def test_pause_running_engine(self, api_client, engine):
        engine.status = EngineStatus.RUNNING
        async with (await api_client()) as client:
            resp = await client.post("/api/pause")
        assert resp.status_code == 200
        assert resp.json()["status"] == EngineStatus.PAUSED.value

    async def test_pause_stopped_engine_returns_409(self, api_client, engine):
        engine.status = EngineStatus.STOPPED
        async with (await api_client()) as client:
            resp = await client.post("/api/pause")
        assert resp.status_code == 409


class TestResumeCollector:

    async def test_resume_paused_engine(self, api_client, engine):
        engine.status = EngineStatus.PAUSED
        engine._pause_event.clear()
        async with (await api_client()) as client:
            resp = await client.post("/api/resume")
        assert resp.status_code == 200
        assert resp.json()["status"] == EngineStatus.RUNNING.value

    async def test_resume_stopped_engine_returns_409(self, api_client, engine):
        engine.status = EngineStatus.STOPPED
        async with (await api_client()) as client:
            resp = await client.post("/api/resume")
        assert resp.status_code == 409


class TestStopCollector:

    async def test_stop_stopped_engine_is_ok(self, api_client, engine):
        engine.status = EngineStatus.STOPPED
        async with (await api_client()) as client:
            resp = await client.post("/api/stop")
        assert resp.status_code == 200

    async def test_stop_running_engine(self, api_client, engine):
        engine.status = EngineStatus.RUNNING
        async with (await api_client()) as client:
            resp = await client.post("/api/stop")
        assert resp.status_code == 200
        assert resp.json()["status"] == EngineStatus.STOPPED.value
