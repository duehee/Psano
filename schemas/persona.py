from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PersonaGenerateRequest(BaseModel):
    force: bool = False
    model: str = "gpt-4o"

class PersonaGenerateResponse(BaseModel):
    ok: bool
    phase: str
    formed_at: Optional[str] = None
    answered_total: int
    axis_scores: Dict[str, int]
    pair_insights: Dict[str, Any]  # 요약/비율/편향 정보
    values_summary: str
    persona_prompt: str
    reused: bool  # 기존 prompt 재사용 여부
    llm_error: Optional[str] = None  # LLM 호출 실패 시 에러 메시지
    used_fallback: bool = False  # fallback 사용 여부
