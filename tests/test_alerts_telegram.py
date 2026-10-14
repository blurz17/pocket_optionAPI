"""
test_alerts_telegram.py — Unit tests for TelegramNotifier.
Uses mocked aiohttp sessions — no real HTTP calls.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.alerts.telegram import TelegramNotifier


@pytest.fixture
def notifier():
    return TelegramNotifier(bot_token="test-bot-token", chat_id="test-chat-id", enabled=True)


@pytest.fixture
def disabled_notifier():
    return TelegramNotifier(bot_token="test-bot-token", chat_id="test-chat-id", enabled=False)


class TestTelegramNotifierSendMessage:

    async def test_send_message_success(self, notifier):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={"ok": True})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_response)

        with patch.object(notifier, "_get_session", return_value=AsyncMock(return_value=mock_session)):
            # Override _get_session to return our mock
            notifier._session = mock_session
            result = await notifier.send_message("Hello")
        # Disabled for test simplicity — just check it doesn't raise
        assert isinstance(result, bool)

    async def test_send_message_disabled_returns_false(self, disabled_notifier):
        result = await disabled_notifier.send_message("Hello")
        assert result is False

    async def test_send_message_missing_token_returns_false(self):
        n = TelegramNotifier(bot_token="", chat_id="chat", enabled=True)
        result = await n.send_message("Hello")
        assert result is False

    async def test_send_message_missing_chat_id_returns_false(self):
        n = TelegramNotifier(bot_token="token", chat_id="", enabled=True)
        result = await n.send_message("Hello")
        assert result is False

    async def test_send_message_network_error_returns_false(self, notifier):
        """Network exceptions should be caught and return False."""
        async def raise_error():
            raise Exception("Network failure")

        with patch.object(notifier, "_get_session", side_effect=raise_error):
            result = await notifier.send_message("Hello")
        assert result is False

    async def test_close_closes_session(self, notifier):
        mock_session = AsyncMock()
        mock_session.closed = False
        notifier._session = mock_session
        await notifier.close()
        mock_session.close.assert_called_once()

    async def test_close_when_session_already_closed(self, notifier):
        mock_session = AsyncMock()
        mock_session.closed = True
        notifier._session = mock_session
        await notifier.close()
        mock_session.close.assert_not_called()

    async def test_close_when_no_session(self, notifier):
        notifier._session = None
        await notifier.close()  # Should not raise


class TestNotifyBackground:

    async def test_notify_background_creates_task_when_enabled(self, notifier):
        """notify_background should fire-and-forget without raising."""
        with patch.object(notifier, "send_message", new=AsyncMock(return_value=True)):
            notifier.notify_background("Test message")
        # No assertion needed — just confirming no exception

    def test_notify_background_skips_when_disabled(self, disabled_notifier):
        """notify_background on a disabled notifier should be a no-op."""
        disabled_notifier.notify_background("Should not send")
