"""
Pocket Option Data Harvester — Launcher

Usage:
    python run_dashboard.py
"""
import os
import logging
import uvicorn
from app.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", config.DASHBOARD_PORT))
    host = os.environ.get("HOST", config.DASHBOARD_HOST)

    tg_status = "Configured" if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID else "Disabled / Pending Config"
    db_target = (
        "PostgreSQL (Neon / Cloud)"
        if not config.USE_SQLITE_FALLBACK and config.DATABASE_URL
        else "Local SQLite Fallback"
    )

    print(rf"""
========================================================================
   POCKET OPTION CONTINUOUS MARKET DATA HARVESTER (AI/ML ENGINE)
========================================================================
  • Web Dashboard Host: http://{host}:{port}
  • Database Target:    {db_target}
  • Telegram Alerts:    {tg_status}
========================================================================
""", flush=True)

    from app.main import app
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )

