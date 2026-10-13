import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    USE_SQLITE_FALLBACK: bool = os.getenv("USE_SQLITE_FALLBACK", "false").lower() in ("true", "1")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "pocket_option_candles.db"))

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "true").lower() in ("true", "1")

    # Pocket Option Credentials & Session
    PO_SESSION: str = os.getenv("PO_SESSION", "")
    PO_UID: int = int(os.getenv("PO_UID", "0"))
    PO_IS_DEMO: int = int(os.getenv("PO_IS_DEMO", "0"))
    PO_PLATFORM: int = int(os.getenv("PO_PLATFORM", "2"))

    # Endpoints
    DEMO_WS_URL: str = "wss://demo-api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    REAL_WS_URL: str = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"

    # Defaults
    DEFAULT_TIMEFRAME: int = int(os.getenv("DEFAULT_TIMEFRAME", "60"))
    DEFAULT_SYMBOLS: list = [s.strip() for s in os.getenv("DEFAULT_SYMBOLS", "EURUSD_otc,GBPUSD_otc,USDJPY_otc,EURUSD").split(",") if s.strip()]

    # Dashboard Server (Dynamically binds to Heroku $PORT if set)
    DASHBOARD_HOST: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    DASHBOARD_PORT: int = int(os.getenv("PORT", os.getenv("DASHBOARD_PORT", "8000")))

config = Config()
