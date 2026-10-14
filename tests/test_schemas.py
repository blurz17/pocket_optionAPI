"""
test_schemas.py — Pydantic schema validation tests.
"""
import pytest
from pydantic import ValidationError
from app.schemas.collector import SessionUpdateRequest, ConfigUpdateRequest


class TestSessionUpdateRequest:

    def test_valid_session(self):
        req = SessionUpdateRequest(session="valid-session-token")
        assert req.session == "valid-session-token"

    def test_session_stripped(self):
        req = SessionUpdateRequest(session="  token  ")
        assert req.session == "token"

    def test_empty_session_raises(self):
        with pytest.raises(ValidationError):
            SessionUpdateRequest(session="")

    def test_whitespace_only_session_raises(self):
        with pytest.raises(ValidationError):
            SessionUpdateRequest(session="   ")

    def test_optional_uid_defaults_to_none(self):
        req = SessionUpdateRequest(session="tok")
        assert req.uid is None

    def test_optional_is_demo_defaults_to_none(self):
        req = SessionUpdateRequest(session="tok")
        assert req.is_demo is None

    def test_uid_and_is_demo_accepted(self):
        req = SessionUpdateRequest(session="tok", uid=12345, is_demo=1)
        assert req.uid == 12345
        assert req.is_demo == 1


class TestConfigUpdateRequest:

    def test_valid_config(self):
        req = ConfigUpdateRequest(timeframe=60, symbols=["EURUSD", "GBPUSD"])
        assert req.timeframe == 60
        assert req.symbols == ["EURUSD", "GBPUSD"]

    def test_zero_timeframe_raises(self):
        with pytest.raises(ValidationError):
            ConfigUpdateRequest(timeframe=0, symbols=["EURUSD"])

    def test_negative_timeframe_raises(self):
        with pytest.raises(ValidationError):
            ConfigUpdateRequest(timeframe=-5, symbols=["EURUSD"])

    def test_empty_symbols_list_raises(self):
        with pytest.raises(ValidationError):
            ConfigUpdateRequest(timeframe=60, symbols=[])

    def test_whitespace_symbols_are_cleaned(self):
        req = ConfigUpdateRequest(timeframe=60, symbols=["EURUSD ", " GBPUSD"])
        assert req.symbols == ["EURUSD", "GBPUSD"]

    def test_blank_symbols_are_removed(self):
        req = ConfigUpdateRequest(timeframe=60, symbols=["EURUSD", "  ", "GBPUSD"])
        assert "  " not in req.symbols
        assert len(req.symbols) == 2

    def test_all_blank_symbols_raises(self):
        with pytest.raises(ValidationError):
            ConfigUpdateRequest(timeframe=60, symbols=["  ", "   "])
