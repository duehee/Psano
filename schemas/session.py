from pydantic import BaseModel, Field
from typing import Optional, Literal
from .common import Phase

EndReason = Literal["completed", "max_reached", "timeout", "admin", "error"]

class SessionStartRequest(BaseModel):
    visitor_name: Optional[str] = Field(None, max_length=100)

class SessionStartResponse(BaseModel):
    session_id: int
    phase: Phase
    current_question: int  # formation일 때 의미 있음

class SessionEndRequest(BaseModel):
    session_id: int
    reason: Optional[EndReason] = "completed"

class SessionEndResponse(BaseModel):
    session_id: int
    ended: bool
    end_reason: Optional[str] = None
    ended_at: Optional[str] = None
    already_ended: bool = False