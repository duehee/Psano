from pydantic import BaseModel, Field
from .common import Status

class TalkRequest(BaseModel):
    session_id: int
    user_text: str = Field(..., min_length=1, max_length=1000)

class TalkResponse(BaseModel):
    status: Status
    ui_text: str  # 화면에 바로 뿌릴 텍스트