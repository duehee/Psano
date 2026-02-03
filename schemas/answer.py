from typing import Optional, Literal

from pydantic import BaseModel

class AnswerRequest(BaseModel):
    session_id: int
    question_id: int
    choice: Literal["A", "B"]

class AnswerResponse(BaseModel):
    ok: bool
    session_should_end: bool
    session_question_index: int
    chosen_value_key: Optional[str] = None
    assistant_reaction_text: str
    next_question: Optional[int] = None
    persona_generated: bool = False  # 365 도달로 페르소나 생성됨