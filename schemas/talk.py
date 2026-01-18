from pydantic import BaseModel, Field
from typing import List, Optional
from .common import Status

class TalkRequest(BaseModel):
    session_id: int
    user_text: str = Field(..., min_length=1, max_length=1000)

class TalkResponse(BaseModel):
    status: Status
    ui_text: str  # 화면에 바로 뿌릴 텍스트

class TopicItem(BaseModel):
    id: int
    title: str
    description: str
    created_at: Optional[str] = None  # ISO string

class TopicsResponse(BaseModel):
    topics: List[TopicItem]