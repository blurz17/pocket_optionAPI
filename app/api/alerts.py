# Pocket Option Data Harvester — Telegram test alert route
from fastapi import APIRouter, Request

alerts_router = APIRouter()


@alerts_router.post("/test-telegram")
async def test_telegram_alert(request: Request):
    """Send a test message to the configured Telegram bot."""
    notifier = request.app.state.notifier
    ok = await notifier.send_message(
        "🧪 *Test Alert:* Pocket Option Harvester Telegram integration is functioning correctly!"
    )
    return {"ok": ok}
