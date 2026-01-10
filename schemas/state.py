# app/schemas/psano_state.py
from pydantic import BaseModel
from typing import Optional, Literal

class StateResponse(BaseModel):
    phase: Literal["formation", "chat"]
    current_question: int
    formed_at: Optional[str] = None  # ISO string