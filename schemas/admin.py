from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Phase = Literal["teach", "talk"]

class AdminPersonalitySetRequest(BaseModel):
    self_direction: int
    conformity: int
    stimulation: int
    security: int
    hedonism: int
    tradition: int
    achievement: int
    benevolence: int
    power: int
    universalism: int

class AdminPersonalitySetResponse(BaseModel):
    ok: bool
    updated: bool

class AdminPersonalityGetResponse(BaseModel):
    self_direction: int
    conformity: int
    stimulation: int
    security: int
    hedonism: int
    tradition: int
    achievement: int
    benevolence: int
    power: int
    universalism: int

class AdminSessionItem(BaseModel):
    id: int
    visitor_name: str
    started_at: str
    ended_at: Optional[str] = None
    end_reason: Optional[str] = None

class AdminSessionsResponse(BaseModel):
    total: int
    sessions: List[AdminSessionItem]

class AdminProgressResponse(BaseModel):
    phase: Phase
    current_question: int         # "지금 열려있는(다음) 질문 번호"
    answered_count: int           # current_question - 1 (formation 기준)
    max_questions: int            # 365
    progress_ratio: float         # 0~1
    global_turn_count: int = 0    # 글로벌 대화 턴 카운트
    global_turn_max: int = 365    # 글로벌 최대 턴

class AdminResetRequest(BaseModel):
    reset_answers: bool = Field(default=False)
    reset_sessions: bool = Field(default=False)
    reset_state: bool = Field(default=True)
    reset_personality: bool = Field(default=False)

class AdminResetResponse(BaseModel):
    ok: bool
    reset_answers: bool
    reset_sessions: bool
    reset_state: bool
    reset_personality: bool

class AdminPhaseSetRequest(BaseModel):
    phase: Phase

class AdminPhaseSetResponse(BaseModel):
    ok: bool
    phase: Phase

class AdminSetCurrentQuestionRequest(BaseModel):
    current_question: int = Field(..., ge=1, le=365)

class AdminSetCurrentQuestionResponse(BaseModel):
    ok: bool
    current_question: int


# =========================
# Import 응답 스키마
# =========================

class ImportErrorItem(BaseModel):
    row: int
    message: str


class AdminQuestionsImportResponse(BaseModel):
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0
    errors: List[ImportErrorItem] = Field(default_factory=list)


class AdminSettingsImportResponse(BaseModel):
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0
    errors: List[ImportErrorItem] = Field(default_factory=list)