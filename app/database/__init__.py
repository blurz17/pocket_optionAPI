from app.config import config
from app.database.postgres import PostgresManager
from app.database.sqlite import SQLiteManager

def get_database():
    if config.USE_SQLITE_FALLBACK or not config.DATABASE_URL:
        return SQLiteManager(config.SQLITE_DB_PATH)
    return PostgresManager(config.DATABASE_URL)

db = get_database()
