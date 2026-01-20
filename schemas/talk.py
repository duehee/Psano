from pydantic import BaseModel, Field
from typing import List, Optional
from .common import Status

class TalkStartRequest(BaseModel):
    session_id: int = Field(..., ge=1)
    topic_id: int = Field(..., ge=1)

    model: str = "gpt-4o-mini"
    max_output_tokens: Optional[int] = None

class TalkStartResponse(BaseModel):
    status: Status
    assistant_first_text: str
    fallback_code: Optional[str] = None

class TalkEndRequest(BaseModel):
    session_id: int

class TalkEndResponse(BaseModel):
    session_id: int
    ended: bool
    already_ended: bool
    end_reason: Optional[str] = None
    ended_at: Optional[str] = None

class TalkRequest(BaseModel):
    session_id: int = Field(..., ge=1)
    user_text: str = Field(..., min_length=1, max_length=200)
    topic_id: Optional[int] = Field(None, ge=1)

    model: str = "gpt-4o-mini"
    max_output_tokens: Optional[int] = None

class TalkResponse(BaseModel):
    status: Status
    ui_text: str
    fallback_code: Optional[str] = None
    policy_category: Optional[str] = None
    should_end: bool = False

class TopicItem(BaseModel):
    id: int
    title: str
    description: str
    created_at: Optional[str] = None  # ISO string

class TopicsResponse(BaseModel):
    topics: List[TopicItem]