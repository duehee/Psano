# app/schemas/question.py
from pydantic import BaseModel, Field

class QuestionResponse(BaseModel):
    id: int
    axis_key: str = Field(..., min_length=1, max_length=50)
    question_text: str
    choice_a: str
    choice_b: str
    enabled: bool = True