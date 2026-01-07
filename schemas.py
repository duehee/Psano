from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field

class InteractionRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: str = Field(default="gpt-4.1-mini")
    max_output_tokens: int = Field(default=150, ge=1, le=2000)

class InteractionResponse(BaseModel):
    reply: str

class BasicStatusResponse(BaseModel):
    ok: bool

class SessionStartResponse(BaseModel):
    session_id: str
    stage: int
    values: Dict[str, Any]

class SessionEndRequest(BaseModel):
    session_id: str
    reason: Literal["completed", "timeout", "admin", "error"] = "completed"

class TeachQuestionResponse(BaseModel):
    question_id: int
    text: str
    a_text: str
    b_text: str

class TeachAnswerRequest(BaseModel):
    session_id: str
    question_id: int
    choice: Literal["A", "B"]

class TalkRequest(BaseModel):
    session_id: str
    user_text: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="gpt-4.1-mini")
    max_output_tokens: int = Field(default=250, ge=1, le=2000)

class UiResponse(BaseModel):
    status: Literal["ok", "fallback", "error"]
    ui_text: str
    stage: int
    values: Dict[str, Any]
    next_action: Optional[str] = None

class StateResponse(BaseModel):
    stage: int
    values: Dict[str, Any]
    total_teach_count: int
    total_talk_count: int