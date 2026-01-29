from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from schemas.common import Status

class MonologueRequest(BaseModel):
    model: str = "gpt-4o"
    max_output_tokens: Optional[int] = None
    answered_total_override: Optional[int] = None

class MonologueResponse(BaseModel):
    status: Status
    monologue_text: str
    fallback_code: Optional[str] = None

    answered_total: int
    stage_id: int
    stage_name_kr: str
    stage_name_en: str


class NudgeRequest(BaseModel):
    """대화 중 nudge 요청 (idle 기반)"""
    session_id: int

    model: str = "gpt-4o"
    max_output_tokens: Optional[int] = None
    recent_messages: Optional[int] = None  # 최근 메시지 수 (기본 6)


class NudgeResponse(BaseModel):
    """대화 중 nudge 응답"""
    status: Status
    nudge_text: str
    fallback_code: Optional[str] = None

    session_id: int
    idle_id: int