# Pocket Option Data Harvester — Database Protocol (abstract interface)
from typing import Protocol, List, Dict, Any, Optional, runtime_checkable


@runtime_checkable
class DatabaseProtocol(Protocol):
    """
    Structural interface for all database backends.
    Both PostgresManager and SQLiteManager must satisfy this protocol.
    This enables type-safe dependency injection without inheritance.
    """

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def save_candles(
        self,
        symbol: str,
        timeframe: int,
        candles: List[Dict[str, Any]],
    ) -> int:
        ...

    async def get_recent_candles(
        self,
        symbol: Optional[str] = None,
        timeframe: int = 60,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        ...

    async def get_total_candles_count(self) -> int:
        ...

    async def get_symbols_summary(self) -> List[Dict[str, Any]]:
        ...
