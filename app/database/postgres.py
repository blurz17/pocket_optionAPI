import asyncio
import asyncpg
import logging
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger("database.postgres")

class PostgresManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        if self.dsn.startswith("postgres://"):
            self.dsn = self.dsn.replace("postgres://", "postgresql://", 1)
        # Clean DSN if channel_binding is present (asyncpg does not accept it as param)
        if "channel_binding" in self.dsn:
            self.dsn = self.dsn.replace("&channel_binding=require", "").replace("channel_binding=require&", "")
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if self.pool is None:
            logger.info("Initializing Neon PostgreSQL connection pool...")
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
                max_inactive_connection_lifetime=300.0,
                command_timeout=60.0
            )
            await self._create_schema()
            logger.info("Neon PostgreSQL connected and schema verified.")

    async def disconnect(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("Neon PostgreSQL connection pool closed.")

    async def _create_schema(self):
        query = """
        CREATE TABLE IF NOT EXISTS candles (
            id BIGSERIAL PRIMARY KEY,
            symbol VARCHAR(32) NOT NULL,
            timeframe INTEGER NOT NULL,
            timestamp BIGINT NOT NULL,
            open NUMERIC(16, 6) NOT NULL,
            high NUMERIC(16, 6) NOT NULL,
            low NUMERIC(16, 6) NOT NULL,
            close NUMERIC(16, 6) NOT NULL,
            volume NUMERIC(16, 2) DEFAULT 0,
            created_at BIGINT NOT NULL,
            CONSTRAINT uq_symbol_tf_ts UNIQUE (symbol, timeframe, timestamp)
        );

        CREATE INDEX IF NOT EXISTS idx_candles_symbol_tf_ts 
        ON candles(symbol, timeframe, timestamp DESC);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query)

    async def save_candles(self, symbol: str, timeframe: int, candles: List[Dict[str, Any]]) -> int:
        """Batch inserts candles with ON CONFLICT DO NOTHING to guarantee deduplication."""
        if not candles or self.pool is None:
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

        query = """
        INSERT INTO candles (symbol, timeframe, timestamp, open, high, low, close, volume, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (symbol, timeframe, timestamp) DO NOTHING;
        """
        async with self.pool.acquire() as conn:
            res = await conn.executemany(query, records)
            return len(records)

    async def get_recent_candles(self, symbol: Optional[str] = None, timeframe: int = 60, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieves newest candles for preview."""
        if self.pool is None:
            return []

        if symbol:
            query = """
            SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
            FROM candles
            WHERE symbol = $1 AND timeframe = $2
            ORDER BY timestamp DESC
            LIMIT $3;
            """
            args = [symbol, timeframe, limit]
        else:
            query = """
            SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
            FROM candles
            ORDER BY timestamp DESC
            LIMIT $1;
            """
            args = [limit]

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]

    async def get_total_candles_count(self) -> int:
        """Returns the total number of records in the database."""
        if self.pool is None:
            return 0
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT count(*) FROM candles;")

    async def get_symbols_summary(self) -> List[Dict[str, Any]]:
        """Returns per-symbol candle counts and latest timestamps."""
        if self.pool is None:
            return []
        query = """
        SELECT symbol, timeframe, count(*) as count, max(timestamp) as latest_ts, min(timestamp) as oldest_ts
        FROM candles
        GROUP BY symbol, timeframe
        ORDER BY count DESC;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(r) for r in rows]
