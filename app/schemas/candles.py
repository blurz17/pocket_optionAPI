# Pocket Option Data Harvester — Pydantic Schemas (candles)
from typing import Optional
from pydantic import BaseModel


class CandleRecord(BaseModel):
    symbol: str
    timeframe: int
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    created_at: int


class CandlesResponse(BaseModel):
    candles: list[CandleRecord]


class StatusResponse(BaseModel):
    status: str
    candles_total: int
    candles_per_min: int
    ticks_total: int
    uptime_seconds: int
    latency_ms: float
    start_time: Optional[float]
    active_symbols: int
    db_type: str
    last_tick_time: Optional[str]
    candles_total_db: int
    session_configured: bool
    uid: int
    is_demo: int
