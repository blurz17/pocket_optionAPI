"""
test_api_session.py — Route integration tests for /api/session endpoint.
"""
import pytest


class TestUpdateSession:

    async def test_valid_session_returns_ok(self, api_client, engine):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={"session": "my-valid-token"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert engine.session_token == "my-valid-token"

    async def test_empty_session_returns_422(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={"session": ""})
        assert resp.status_code == 422

    async def test_whitespace_session_returns_422(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={"session": "   "})
        assert resp.status_code == 422

    async def test_missing_session_field_returns_422(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={})
        assert resp.status_code == 422

    async def test_session_with_uid_and_is_demo(self, api_client, engine):
        async with (await api_client()) as client:
            resp = await client.post("/api/session", json={
                "session": "tok",
                "uid": 99999,
                "is_demo": 0,
            })
        assert resp.status_code == 200
        assert engine.uid == 99999
        assert engine.is_demo == 0


class TestUpdateConfig:

    async def test_valid_config_returns_ok(self, api_client, engine):
        async with (await api_client()) as client:
            resp = await client.post("/api/config", json={
                "timeframe": 300,
                "symbols": ["EURUSD", "GBPUSD"],
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["timeframe"] == 300
        assert engine.timeframe == 300

    async def test_zero_timeframe_rejected(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/config", json={"timeframe": 0, "symbols": ["EURUSD"]})
        assert resp.status_code == 422

    async def test_empty_symbols_rejected(self, api_client):
        async with (await api_client()) as client:
            resp = await client.post("/api/config", json={"timeframe": 60, "symbols": []})
        assert resp.status_code == 422
