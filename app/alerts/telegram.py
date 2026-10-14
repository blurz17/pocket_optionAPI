# Pocket Option Data Harvester — Telegram Notifier (refactored with httpx)
import asyncio
import logging
from typing import Optional, Any
import httpx

from app.config import config

logger = logging.getLogger("alerts.telegram")


class TelegramNotifier:
    """
    Sends Telegram notifications for harvester lifecycle events.
    No module-level singleton — injected via app.state in main.py.
    """

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.enabled = enabled if enabled is not None else config.TELEGRAM_ENABLED
        self._client: Optional[Any] = None

    async def _get_client(self) -> Any:
        if self._client is None or getattr(self._client, "is_closed", False) or getattr(self._client, "closed", False):
            self._client = httpx.AsyncClient(timeout=8.0)
        return self._client

    async def _get_session(self) -> Any:
        return await self._get_client()

    @property
    def _session(self):
        return self._client

    @_session.setter
    def _session(self, val):
        self._client = val

    async def close(self) -> None:
        if self._client:
            if hasattr(self._client, "aclose") and not getattr(self._client, "is_closed", False):
                await self._client.aclose()
            elif hasattr(self._client, "close") and not getattr(self._client, "closed", False):
                res = self._client.close()
                if asyncio.iscoroutine(res):
                    await res

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        if not self.enabled or not self.bot_token or not self.chat_id:
            logger.debug("Telegram alert skipped (disabled or missing credentials).")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}

        try:
            client = await self._get_client()
            resp = await client.post(url, json=payload)
            # Support both httpx sync .json() and mocked async .json()
            data = resp.json()
            if asyncio.iscoroutine(data):
                data = await data
            if data.get("ok"):
                logger.debug("Telegram alert delivered successfully.")
                return True
            else:
                logger.warning(f"Telegram API returned error: {data}")
                return False
        except Exception as e:
            logger.error(f"Failed to dispatch Telegram alert: {e}")
            return False

    def notify_background(self, text: str) -> None:
        """Dispatches notification without blocking the caller."""
        if self.enabled:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.send_message(text), name="telegram-notify")
            except RuntimeError:
                pass


    async def alert_started(self, symbols: list, timeframe: int, db_type: str) -> None:
        text = (
            f"🚀 *Pocket Option Harvester: STARTED*\n\n"
            f"• *Database:* {db_type}\n"
            f"• *Timeframe:* {timeframe}s\n"
            f"• *Symbols ({len(symbols)}):* {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}\n"
            f"• *Status:* Collecting live candles..."
        )
        await self.send_message(text)

    async def alert_stopped(self, reason: str = "Manual Stop") -> None:
        await self.send_message(f"🛑 *Pocket Option Harvester: STOPPED*\n\n• *Reason:* {reason}")

    async def alert_disconnected(self, attempt: int, delay_s: float) -> None:
        text = (
            f"⚠️ *Harvester Disconnected*\n\n"
            f"• *Reconnection Attempt:* #{attempt}\n"
            f"• *Retrying in:* {delay_s:.1f}s"
        )
        await self.send_message(text)

    async def alert_recovered(self, symbol: str, backfilled_count: int) -> None:
        text = (
            f"✅ *Harvester Reconnected & Recovered*\n\n"
            f"• *Symbol:* `{symbol}`\n"
            f"• *Backfilled Candles:* {backfilled_count}"
        )
        await self.send_message(text)

    async def alert_auth_expired(self) -> None:
        text = (
            f"🚨 *CRITICAL: Pocket Option Session Expired*\n\n"
            f"The broker server rejected authentication (`41 Unauthorized`).\n"
            f"Please update the session token in the Web Dashboard."
        )
        await self.send_message(text)
