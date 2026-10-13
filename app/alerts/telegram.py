import asyncio
import logging
import aiohttp
from typing import Optional
from app.config import config

logger = logging.getLogger("alerts.telegram")

class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None, enabled: bool = True):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.enabled = enabled if enabled is not None else config.TELEGRAM_ENABLED
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            logger.debug("Telegram alert skipped (disabled or missing credentials).")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            session = await self._get_session()
            async with session.post(url, json=payload, timeout=8.0) as resp:
                data = await resp.json()
                if data.get("ok"):
                    logger.debug("Telegram alert delivered successfully.")
                    return True
                else:
                    logger.warning(f"Telegram API returned error: {data}")
                    return False
        except Exception as e:
            logger.error(f"Failed to dispatch Telegram alert: {e}")
            return False

    def notify_background(self, text: str):
        """Dispatches notification without blocking caller."""
        if self.enabled:
            asyncio.create_task(self.send_message(text))

    async def alert_started(self, symbols: list, timeframe: int, db_type: str):
        text = (
            f"🚀 *Pocket Option Harvester: STARTED*\n\n"
            f"• *Database:* {db_type}\n"
            f"• *Timeframe:* {timeframe}s\n"
            f"• *Symbols ({len(symbols)}):* {', '.join(symbols[:5])}{'...' if len(symbols)>5 else ''}\n"
            f"• *Status:* Collecting live candles..."
        )
        await self.send_message(text)

    async def alert_stopped(self, reason: str = "Manual Stop"):
        text = f"🛑 *Pocket Option Harvester: STOPPED*\n\n• *Reason:* {reason}"
        await self.send_message(text)

    async def alert_disconnected(self, attempt: int, delay_s: float):
        text = (
            f"⚠️ *Harvester Disconnected*\n\n"
            f"• *Reconnection Attempt:* #{attempt}\n"
            f"• *Retrying in:* {delay_s:.1f}s"
        )
        await self.send_message(text)

    async def alert_recovered(self, symbol: str, backfilled_count: int):
        text = (
            f"✅ *Harvester Reconnected & Recovered*\n\n"
            f"• *Symbol:* `{symbol}`\n"
            f"• *Backfilled Candles:* {backfilled_count}"
        )
        await self.send_message(text)

    async def alert_auth_expired(self):
        text = (
            f"🚨 *CRITICAL: Pocket Option Session Expired*\n\n"
            f"The broker server rejected authentication (`41 Unauthorized`).\n"
            f"Please update the session token in the Web Dashboard."
        )
        await self.send_message(text)

notifier = TelegramNotifier()
