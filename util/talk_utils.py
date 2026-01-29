"""
Talk/Monologue 공통 유틸리티 함수
- 여러 라우터에서 사용하는 공통 함수들
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.common import Status
from routers.talk_policy import moderate_text, generate_policy_response, Action
from util.utils import trim


OUTPUT_LIMIT = 150


def apply_policy_guard(db: Session, text_for_check: str, user_text: str = ""):
    """
    정책 필터 적용
    CRISIS(자해/자살)와 PRIVACY(개인정보 regex)만 즉시 차단.
    나머지(성적/혐오/범죄/정치/종교)는 LLM이 프롬프트 가이드에 따라 자연스럽게 처리.

    return: None (정상) or dict(policy_response_fields...)
    """
    hit = moderate_text(db, text_for_check)
    if not hit:
        return None

    rule, _kw = hit

    # CRISIS나 PRIVACY만 즉시 차단 (나머지는 LLM이 처리)
    if rule.action not in (Action.CRISIS, Action.PRIVACY):
        return None

    # GPT가 사노 스타일로 응답 생성
    msg, should_end = generate_policy_response(db, rule, user_text or text_for_check)

    return {
        "status": Status.fallback,
        "assistant_text": trim(msg, OUTPUT_LIMIT),
        "fallback_code": f"POLICY_{rule.category.upper()}",
        "policy_category": rule.category,
        "should_end": should_end,
    }