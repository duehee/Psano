from pydantic import BaseModel
from typing import Optional, Literal, Dict

class StateResponse(BaseModel):
    phase: Literal["teach", "talk"]

    current_question: int

    answered_total: int
    axis_scores: Dict[str, int]

    talk_unlocked: Optional[bool] = None
    formed_at: Optional[str] = None
    persona_prompt: Optional[str] = None
