# Pocket Option Data Harvester — Candles data & export routes
import io
import csv
from typing import Optional
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

candles_router = APIRouter()


@candles_router.get("/candles")
async def get_recent_candles(
    request: Request,
    symbol: Optional[str] = None,
    limit: int = 25,
):
    """Return recent OHLCV candles from the database."""
    engine = request.app.state.engine
    db = request.app.state.db
    candles = await db.get_recent_candles(
        symbol=symbol,
        timeframe=engine.timeframe,
        limit=limit,
    )
    return {"candles": candles}


@candles_router.get("/symbols")
async def get_symbols_summary(request: Request):
    """Return per-symbol candle counts and time ranges."""
    db = request.app.state.db
    return {"symbols": await db.get_symbols_summary()}


@candles_router.get("/export")
async def export_csv(
    request: Request,
    symbol: Optional[str] = None,
    limit: int = 5000,
):
    """Stream a CSV export of recent candles."""
    engine = request.app.state.engine
    db = request.app.state.db
    candles = await db.get_recent_candles(
        symbol=symbol,
        timeframe=engine.timeframe,
        limit=limit,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume", "created_at"])
    for c in candles:
        writer.writerow([
            c["symbol"], c["timeframe"], c["timestamp"],
            c["open"], c["high"], c["low"], c["close"],
            c["volume"], c["created_at"],
        ])
    output.seek(0)

    filename = f"pocket_option_candles_{symbol or 'all'}_{engine.timeframe}s.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
