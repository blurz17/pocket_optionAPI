"""
test_normalizer.py — Unit tests for CandleNormalizer.
No I/O, no async, pure logic.
"""
import time
import pytest
from app.collector.normalizer import CandleNormalizer


# ── normalize_closed_candles ──────────────────────────────────────────────────

class TestNormalizeClosedCandles:

    def test_empty_input_returns_empty(self):
        assert CandleNormalizer.normalize_closed_candles([], timeframe=60) == []

    def test_filters_out_forming_bar(self):
        now = int(time.time())
        forming_ts = (now // 60) * 60  # current bar boundary
        candles = [{"time": forming_ts, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5}]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert result == []

    def test_keeps_closed_bars(self):
        now = int(time.time())
        closed_ts = ((now // 60) - 2) * 60  # 2 bars ago
        candles = [{"time": closed_ts, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5}]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert len(result) == 1
        assert result[0]["time"] == closed_ts

    def test_deduplicates_same_timestamp(self):
        now = int(time.time())
        closed_ts = ((now // 60) - 1) * 60
        candles = [
            {"time": closed_ts, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5},
            {"time": closed_ts, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5},
        ]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert len(result) == 1

    def test_integrity_check_fixes_high_low(self):
        """high must be >= open,close; low must be <= open,close."""
        now = int(time.time())
        closed_ts = ((now // 60) - 1) * 60
        # Deliberately broken: high < open, low > close
        candles = [{"time": closed_ts, "open": 1.2, "high": 1.0, "low": 1.3, "close": 1.15, "volume": 5}]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert len(result) == 1
        c = result[0]
        assert c["high"] >= c["open"]
        assert c["high"] >= c["close"]
        assert c["low"] <= c["open"]
        assert c["low"] <= c["close"]

    def test_skips_zero_timestamp(self):
        now = int(time.time())
        candles = [{"time": 0, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5}]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert result == []

    def test_sorted_by_timestamp(self):
        now = int(time.time())
        t1 = ((now // 60) - 3) * 60
        t2 = ((now // 60) - 2) * 60
        candles = [
            {"time": t2, "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 5},
            {"time": t1, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 3},
        ]
        result = CandleNormalizer.normalize_closed_candles(candles, timeframe=60, current_server_time=now)
        assert result[0]["time"] == t1
        assert result[1]["time"] == t2


# ── ticks_to_candles ──────────────────────────────────────────────────────────

class TestTicksToCandles:

    def test_empty_ticks_returns_empty(self):
        assert CandleNormalizer.ticks_to_candles([], timeframe=60) == []

    def test_single_tick_creates_single_candle(self):
        ticks = [(1700000010, 1.1000)]
        result = CandleNormalizer.ticks_to_candles(ticks, timeframe=60)
        assert len(result) == 1
        c = result[0]
        assert c["open"] == 1.1000
        assert c["close"] == 1.1000
        assert c["high"] == 1.1000
        assert c["low"] == 1.1000
        assert c["volume"] == 1.0

    def test_multiple_ticks_same_bar_aggregate(self):
        # Use a bar_start that's exactly divisible by 60 so all 4 offsets stay inside it
        bar_start = (1700000000 // 60) * 60  # floor to bar boundary
        ticks = [
            (bar_start + 1, 1.1000),
            (bar_start + 10, 1.1050),
            (bar_start + 30, 1.0980),
            (bar_start + 50, 1.1020),
        ]
        result = CandleNormalizer.ticks_to_candles(ticks, timeframe=60)
        assert len(result) == 1
        c = result[0]
        assert c["open"] == 1.1000
        assert c["high"] == 1.1050
        assert c["low"] == 1.0980
        assert c["close"] == 1.1020
        assert c["volume"] == 4.0

    def test_ticks_across_two_bars(self):
        bar1 = 1700000000
        bar2 = 1700000060
        ticks = [
            (bar1 + 5, 1.10),
            (bar1 + 30, 1.11),
            (bar2 + 5, 1.12),
            (bar2 + 30, 1.13),
        ]
        result = CandleNormalizer.ticks_to_candles(ticks, timeframe=60)
        assert len(result) == 2
