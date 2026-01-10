from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Phase = Literal["formation", "chat"]

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
    max_questions: int            # 380
    progress_ratio: float         # 0~1

class AdminResetRequest(BaseModel):
    reset_answers: bool = Field(default=False)
    reset_sessions: bool = Field(default=False)
    reset_state: bool = Field(default=True)

class AdminResetResponse(BaseModel):
    ok: bool
    reset_answers: bool
    reset_sessions: bool
    reset_state: bool

class AdminPhaseSetRequest(BaseModel):
    phase: Phase

class AdminPhaseSetResponse(BaseModel):
    ok: bool
    phase: Phase

class AdminSetCurrentQuestionRequest(BaseModel):
    current_question: int = Field(..., ge=1, le=380)

class AdminSetCurrentQuestionResponse(BaseModel):
    ok: bool
    current_question: int