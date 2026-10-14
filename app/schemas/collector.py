# Pocket Option Data Harvester — Pydantic Schemas (collector)
from typing import List, Optional
from pydantic import BaseModel, field_validator


class SessionUpdateRequest(BaseModel):
    session: str
    uid: Optional[int] = None
    is_demo: Optional[int] = None

    @field_validator("session")
    @classmethod
    def session_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("session must not be empty")
        return v.strip()


class ConfigUpdateRequest(BaseModel):
    timeframe: int
    symbols: List[str]

    @field_validator("timeframe")
    @classmethod
    def timeframe_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("timeframe must be a positive integer (seconds)")
        return v

    @field_validator("symbols")
    @classmethod
    def symbols_must_not_be_empty_list(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s.strip()]
        if not cleaned:
            raise ValueError("symbols list must not be empty")
        return cleaned
