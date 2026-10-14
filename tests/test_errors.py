"""
test_errors.py — Tests for core error handlers and custom exceptions.
"""
import pytest
from app.core.errors import (
    AppError,
    CollectorAlreadyRunning,
    CollectorNotRunning,
    SessionRequired,
    DatabaseNotConnected,
)


class TestExceptionHierarchy:

    def test_collector_already_running_is_app_error(self):
        assert issubclass(CollectorAlreadyRunning, AppError)

    def test_collector_not_running_is_app_error(self):
        assert issubclass(CollectorNotRunning, AppError)

    def test_session_required_is_app_error(self):
        assert issubclass(SessionRequired, AppError)

    def test_database_not_connected_is_app_error(self):
        assert issubclass(DatabaseNotConnected, AppError)

    def test_raise_and_catch_as_app_error(self):
        with pytest.raises(AppError):
            raise CollectorAlreadyRunning("Already running")


class TestErrorHandlerRoutes:

    async def test_collector_already_running_returns_409(self, api_client, engine):
        from app.collector.engine import EngineStatus
        engine.status = EngineStatus.RUNNING
        async with (await api_client()) as client:
            resp = await client.post("/api/start")
        assert resp.status_code == 409
        body = resp.json()
        assert "detail" in body
        assert body["detail"]["error_code"] == "collector_already_running"

    async def test_collector_not_running_pause_returns_409(self, api_client, engine):
        from app.collector.engine import EngineStatus
        engine.status = EngineStatus.STOPPED
        async with (await api_client()) as client:
            resp = await client.post("/api/pause")
        assert resp.status_code == 409
        body = resp.json()
        assert body["detail"]["error_code"] == "collector_not_running"

    async def test_validation_error_returns_422(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={"session": ""})
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body

    async def test_health_check_returns_healthy(self, api_client):
        async with (await api_client()) as client:
            resp = await client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
