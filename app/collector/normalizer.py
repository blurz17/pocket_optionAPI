import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("collector.normalizer")

class CandleNormalizer:
    @staticmethod
    def normalize_closed_candles(
        candles: List[Dict[str, Any]], 
        timeframe: int, 
        current_server_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Filters out forming/in-progress candles to ensure zero lookahead bias for AI/ML.
        
        Only candles whose interval has strictly closed are returned:
        candle['time'] + timeframe <= current_server_time
        """
        if not candles:
            return []

        now = current_server_time or int(time.time())
        current_forming_boundary = (now // timeframe) * timeframe

        finalized = []
        for c in candles:
            ts = int(c.get("time") or c.get("timestamp", 0))
            if ts <= 0:
                continue

            # Skip forming bar
            if ts >= current_forming_boundary:
                continue

            o = float(c.get("open", 0.0))
            h = float(c.get("high", 0.0))
            l = float(c.get("low", 0.0))
            cl = float(c.get("close", 0.0))
            vol = float(c.get("volume", 0.0)) if c.get("volume") is not None else 0.0

            # Integrity check: High must be >= Open, Close, Low
            h = max(h, o, cl)
            l = min(l, o, cl)

            finalized.append({
                "time": ts,
                "open": o,
                "high": h,
                "low": l,
                "close": cl,
                "volume": vol,
                "is_synthetic": True, # Pocket Option OTC volume is tick count
            })

        # Deduplicate and sort by timestamp
        finalized.sort(key=lambda x: x["time"])
        seen = set()
        deduped = []
        for c in finalized:
            if c["time"] not in seen:
                seen.add(c["time"])
                deduped.append(c)

        return deduped

    @staticmethod
    def ticks_to_candles(ticks: List[tuple], timeframe: int) -> List[Dict[str, Any]]:
        """Aggregates sub-minute raw stream ticks into standard OHLCV candles."""
        if not ticks:
            return []

        candles_map: Dict[int, Dict[str, Any]] = {}
        for item in sorted(ticks, key=lambda x: x[0]):
            ts, price = float(item[0]), float(item[1])
            bar_start = int((ts // timeframe) * timeframe)

            if bar_start not in candles_map:
                candles_map[bar_start] = {
                    "time": bar_start,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 1.0,
                }
            else:
                b = candles_map[bar_start]
                b["high"] = max(b["high"], price)
                b["low"] = min(b["low"], price)
                b["close"] = price
                b["volume"] += 1.0

        return list(candles_map.values())
