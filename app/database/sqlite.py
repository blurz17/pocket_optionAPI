import sqlite3
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("database.sqlite")

class SQLiteManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_schema()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_schema(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_candles_sqlite ON candles(symbol, timeframe, timestamp DESC);")
        conn.commit()
        conn.close()

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def save_candles(self, symbol: str, timeframe: int, candles: List[Dict[str, Any]]) -> int:
        if not candles:
            return 0
        conn = self._get_conn()
        cur = conn.cursor()
        now = int(time.time())
        inserted = 0
        for c in candles:
            ts = int(c.get("time") or c.get("timestamp", 0))
            if ts <= 0:
                continue
            o = float(c.get("open", 0.0))
            h = float(c.get("high", 0.0))
            l = float(c.get("low", 0.0))
            cl = float(c.get("close", 0.0))
            v = float(c.get("volume", 0.0)) if c.get("volume") is not None else 0.0
            cur.execute("""
                INSERT OR IGNORE INTO candles 
                (symbol, timeframe, timestamp, open, high, low, close, volume, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, timeframe, ts, o, h, l, cl, v, now))
            if cur.rowcount > 0:
                inserted += 1
        conn.commit()
        conn.close()
        return inserted

    async def get_recent_candles(self, symbol: Optional[str] = None, timeframe: int = 60, limit: int = 25) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        if symbol:
            cur.execute("""
                SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
                FROM candles WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (symbol, timeframe, limit))
        else:
            cur.execute("""
                SELECT symbol, timeframe, timestamp, open, high, low, close, volume, created_at
                FROM candles ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    async def get_total_candles_count(self) -> int:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM candles;")
        val = cur.fetchone()[0]
        conn.close()
        return val

    async def get_symbols_summary(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, timeframe, count(*) as count, max(timestamp) as latest_ts, min(timestamp) as oldest_ts
            FROM candles GROUP BY symbol, timeframe ORDER BY count DESC;
        """)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
