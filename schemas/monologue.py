from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from schemas.common import Status

class MonologueRequest(BaseModel):
    model: str = "gpt-4o-mini"
    max_output_tokens: Optional[int] = None
    answered_total_override: Optional[int] = None

class MonologueResponse(BaseModel):
    status: Status
    monologue_text: str
    fallback_code: Optional[str] = None

    answered_total: int
    stage_id: int
    stage_name_kr: str
    stage_name_en: str