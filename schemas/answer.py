# app/schemas/answer.py
from enum import Enum
from pydantic import BaseModel, Field

class Choice(str, Enum):
    A = "A"
    B = "B"

class AnswerRequest(BaseModel):
    session_id: int
    question_id: int
    choice: Choice

class AnswerResponse(BaseModel):
    saved: bool = True
    next_question: int | None = None  # 다음 질문 id (formation에서만)