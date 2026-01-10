from pydantic import BaseModel, Field
from .common import Phase

class SessionStartRequest(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=100)

class SessionStartResponse(BaseModel):
    session_id: int
    phase: Phase
    current_question: int  # formation일 때 의미 있음

class SessionEndRequest(BaseModel):
    session_id: int
    reason: str | None = Field(default=None, max_length=32)

class SessionEndResponse(BaseModel):
    session_id: int
    ended: bool = True