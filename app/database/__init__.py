# Pocket Option Data Harvester — Database factory
from app.config import config
from app.database.sqlite import SQLiteManager
from app.database.base import DatabaseProtocol


def get_database() -> DatabaseProtocol:
    """
    Returns the appropriate database backend based on configuration.
    - Uses PostgreSQL if DATABASE_URL is set and USE_SQLITE_FALLBACK is False.
    - Falls back to SQLite otherwise.
    """
    if config.USE_SQLITE_FALLBACK or not config.DATABASE_URL:
        return SQLiteManager(config.SQLITE_DB_PATH)
    from app.database.postgres import PostgresManager
    return PostgresManager(config.DATABASE_URL)


__all__ = ["get_database", "DatabaseProtocol"]

