"""
test_database_sqlite.py — Integration tests for SQLiteManager (aiosqlite).
Uses real temp file DB — no mocks.
"""
import pytest


class TestSQLiteManagerConnect:

    async def test_connect_creates_schema(self, sqlite_db):
        """connect() should create the candles table without error."""
        # If schema creation failed, save_candles would fail
        result = await sqlite_db.save_candles("EURUSD", 60, [])
        assert result == 0


class TestSQLiteManagerSaveCandles:

    async def test_save_empty_list_returns_zero(self, sqlite_db):
        count = await sqlite_db.save_candles("EURUSD", 60, [])
        assert count == 0

    async def test_save_valid_candles_returns_count(self, sqlite_db, sample_candles):
        count = await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        assert count == len(sample_candles)

    async def test_save_duplicate_candles_idempotent(self, sqlite_db, sample_candles):
        """Inserting same candles twice should not increase count."""
        count1 = await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        count2 = await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        assert count1 == len(sample_candles)
        assert count2 == 0  # ON CONFLICT IGNORE: no new rows

    async def test_skips_candles_with_zero_timestamp(self, sqlite_db):
        bad_candles = [{"time": 0, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.1, "volume": 1}]
        count = await sqlite_db.save_candles("EURUSD", 60, bad_candles)
        assert count == 0

    async def test_save_uses_timestamp_key(self, sqlite_db):
        """Candles may use 'timestamp' key instead of 'time'."""
        candles = [{"timestamp": 1700001000, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.1, "volume": 5}]
        count = await sqlite_db.save_candles("EURUSD", 60, candles)
        assert count == 1


class TestSQLiteManagerGetCandles:

    async def test_get_recent_candles_empty_db(self, sqlite_db):
        result = await sqlite_db.get_recent_candles()
        assert result == []

    async def test_get_recent_candles_after_insert(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        result = await sqlite_db.get_recent_candles(symbol="EURUSD", timeframe=60, limit=10)
        assert len(result) == len(sample_candles)

    async def test_get_candles_filtered_by_symbol(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        await sqlite_db.save_candles("GBPUSD", 60, sample_candles)
        result = await sqlite_db.get_recent_candles(symbol="EURUSD", timeframe=60)
        assert all(r["symbol"] == "EURUSD" for r in result)

    async def test_get_candles_respects_limit(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        result = await sqlite_db.get_recent_candles(limit=1)
        assert len(result) == 1

    async def test_candle_fields_present(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        result = await sqlite_db.get_recent_candles(symbol="EURUSD", timeframe=60)
        assert len(result) > 0
        row = result[0]
        for field in ["symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume", "created_at"]:
            assert field in row, f"Missing field: {field}"


class TestSQLiteManagerCount:

    async def test_total_count_empty(self, sqlite_db):
        count = await sqlite_db.get_total_candles_count()
        assert count == 0

    async def test_total_count_after_insert(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        count = await sqlite_db.get_total_candles_count()
        assert count == len(sample_candles)

    async def test_symbols_summary_empty(self, sqlite_db):
        result = await sqlite_db.get_symbols_summary()
        assert result == []

    async def test_symbols_summary_after_insert(self, sqlite_db, sample_candles):
        await sqlite_db.save_candles("EURUSD", 60, sample_candles)
        result = await sqlite_db.get_symbols_summary()
        assert len(result) == 1
        assert result[0]["symbol"] == "EURUSD"
        assert result[0]["count"] == len(sample_candles)
