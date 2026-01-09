# app/schemas/state.py
from pydantic import BaseModel
from .common import Phase

class StateResponse(BaseModel):
    phase: Phase
    current_question: int
    formed_at: str | None = None  # 간단히 string(ISO)로