from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id: int
    axis_key: str
    question_text: str
    choice_a: str
    choice_b: str
    enabled: bool