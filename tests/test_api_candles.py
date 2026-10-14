"""
test_api_candles.py — Route integration tests for /api/candles and /api/export.
"""
import pytest


class TestGetCandles:

    async def test_returns_empty_list_from_mock(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/candles")
        assert resp.status_code == 200
        assert resp.json() == {"candles": []}

    async def test_returns_candles_from_db(self, api_client, mock_db, sample_candles):
        db_rows = [
            {**c, "symbol": "EURUSD", "timeframe": 60, "timestamp": c["time"], "created_at": 1700000200}
            for c in sample_candles
        ]
        mock_db.get_recent_candles.return_value = db_rows
        async with (await api_client()) as client:
            resp = await client.get("/api/candles")
        data = resp.json()
        assert len(data["candles"]) == len(sample_candles)

    async def test_symbol_filter_passed_to_db(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            await client.get("/api/candles?symbol=EURUSD")
        call_kwargs = mock_db.get_recent_candles.call_args
        assert call_kwargs.kwargs.get("symbol") == "EURUSD"

    async def test_limit_passed_to_db(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            await client.get("/api/candles?limit=10")
        call_kwargs = mock_db.get_recent_candles.call_args
        assert call_kwargs.kwargs.get("limit") == 10


class TestExportCsv:

    async def test_export_returns_csv_content_type(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/export")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    async def test_export_has_content_disposition(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/export")
        assert "attachment" in resp.headers.get("content-disposition", "")

    async def test_export_csv_has_header_row(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/export")
        content = resp.text
        assert "symbol" in content
        assert "open" in content
        assert "close" in content

    async def test_export_csv_with_candles(self, api_client, mock_db, sample_candles):
        db_rows = [
            {**c, "symbol": "EURUSD", "timeframe": 60, "timestamp": c["time"], "created_at": 1700000200}
            for c in sample_candles
        ]
        mock_db.get_recent_candles.return_value = db_rows
        async with (await api_client()) as client:
            resp = await client.get("/api/export?symbol=EURUSD")
        lines = resp.text.strip().split("\n")
        # Header + 3 data rows
        assert len(lines) == 4

    async def test_export_filename_includes_symbol(self, api_client, mock_db):
        mock_db.get_recent_candles.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/export?symbol=GBPUSD")
        disposition = resp.headers.get("content-disposition", "")
        assert "GBPUSD" in disposition


class TestGetSymbolsSummary:

    async def test_symbols_returns_empty(self, api_client, mock_db):
        mock_db.get_symbols_summary.return_value = []
        async with (await api_client()) as client:
            resp = await client.get("/api/symbols")
        assert resp.status_code == 200
        assert resp.json() == {"symbols": []}

    async def test_symbols_returns_data(self, api_client, mock_db):
        mock_db.get_symbols_summary.return_value = [
            {"symbol": "EURUSD", "timeframe": 60, "count": 100, "latest_ts": 1700000120, "oldest_ts": 1700000000}
        ]
        async with (await api_client()) as client:
            resp = await client.get("/api/symbols")
        data = resp.json()
        assert len(data["symbols"]) == 1
        assert data["symbols"][0]["symbol"] == "EURUSD"
