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

    # 글로벌 엔딩 관련
    global_turn_count: Optional[int] = None
    global_turn_max: Optional[int] = None
    global_ended: Optional[bool] = None

    # 사이클
    cycle_number: Optional[int] = None
