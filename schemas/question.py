from typing import Optional

from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id: int
    axis_key: str
    question_text: str
    choice_a: str
    choice_b: str
    enabled: bool

    session_question_index: int

    value_a_key: Optional[str] = None
    value_b_key: Optional[str] = None