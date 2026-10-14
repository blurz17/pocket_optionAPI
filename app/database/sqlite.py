# Pocket Option Data Harvester — SQLite Database Manager (true async via aiosqlite)
import time
import logging
import aiosqlite
from typing import List, Dict, Any, Optional

logger = logging.getLogger("database.sqlite")


class SQLiteManager:
    """
    Async SQLite database backend using aiosqlite.
    Uses the same interface as PostgresManager (DatabaseProtocol).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def connect(self) -> None:
        """Create schema on first connect."""
        await self._create_schema()
        logger.info(f"SQLite database ready: {self.db_path}")

    async def disconnect(self) -> None:
        """No persistent connection to close (aiosqlite opens per-operation)."""
        logger.info("SQLite disconnected (stateless).")

    async def _create_schema(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS candles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL DEFAULT 0,
                    created_at INTEGER NOT NULL,
                    UNIQUE (symbol, timeframe, timestamp)
                );
            """)
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_candles_sqlite "
                "ON candles(symbol, timeframe, timestamp DESC);"
            )
            await db.commit()

    async def save_candles(
        self,
        symbol: str,
        timeframe: int,
        candles: List[Dict[str, Any]],
    ) -> int:
        if not candles:
            return 0

        now = int(time.time())
        records = []
        for c in candles:
            ts = int(c.get("time") or c.get("timestamp", 0))
            if ts <= 0:
                continue
            o = float(c.get("open", 0.0))
            h = float(c.get("high", 0.0))
            l = float(c.get("low", 0.0))
            cl = float(c.get("close", 0.0))
            v = float(c.get("volume", 0.0)) if c.get("volume") is not None else 0.0
            records.append((symbol, timeframe, ts, o, h, l, cl, v, now))

        if not records:
            return 0

        inserted = 0
        async with aiosqlite.connect(self.db_path) as db:
            for record in records:
                cursor = await db.execute(
                    """
                    INSERT OR IGNORE INTO candles
                    (symbol, timeframe, timestamp, open, high, low, close, volume, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    record,
                )
                if cursor.rowcount > 0:
                    inserted += 1
            await db.commit()

        return inserted

    async def get_recent_candles(
        self,
        symbol: Optional[str] = None,
        timeframe: int = 60,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if symbol:
                cursor = await db.execute(
                    """
                    SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
                    FROM candles WHERE symbol = ? AND timeframe = ?
                    ORDER BY timestamp DESC LIMIT ?
                    """,
                    (symbol, timeframe, limit),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
                    FROM candles ORDER BY timestamp DESC LIMIT ?
                    """,
                    (limit,),
                )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_total_candles_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT count(*) FROM candles;")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_symbols_summary(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT symbol, timeframe, count(*) as count,
                       max(timestamp) as latest_ts, min(timestamp) as oldest_ts
                FROM candles GROUP BY symbol, timeframe ORDER BY count DESC;
            """)
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
