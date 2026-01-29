from pydantic import BaseModel, Field
from typing import Optional
from .common import Status


class TalkStartRequest(BaseModel):
    """대화 시작 요청 (idle 기반)"""
    session_id: int = Field(..., ge=1)
    idle_id: int = Field(..., ge=1)  # 혼잣말 ID (/idle/random에서 받은 값)

    model: str = "gpt-4o-mini"
    max_output_tokens: Optional[int] = None


class TalkStartResponse(BaseModel):
    """대화 시작 응답"""
    status: Status
    assistant_first_text: str
    idle_text: str  # 원본 혼잣말 텍스트
    fallback_code: Optional[str] = None


class TalkTurnRequest(BaseModel):
    """대화 턴 요청"""
    session_id: int = Field(..., ge=1)
    user_text: str = Field(..., min_length=1, max_length=200)

    model: str = "gpt-4o-mini"
    max_output_tokens: Optional[int] = None


class TalkTurnResponse(BaseModel):
    """대화 턴 응답"""
    status: Status
    ui_text: str
    fallback_code: Optional[str] = None
    policy_category: Optional[str] = None
    should_end: bool = False
    # 글로벌 엔딩 관련
    warning_text: Optional[str] = None  # 예고 메시지 (355~364)
    global_ended: bool = False  # 글로벌 엔딩 (365)


class TalkEndRequest(BaseModel):
    """대화 종료 요청"""
    session_id: int


class TalkEndResponse(BaseModel):
    """대화 종료 응답"""
    session_id: int
    ended: bool
    already_ended: bool
    end_reason: Optional[str] = None
    ended_at: Optional[str] = None