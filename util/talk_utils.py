"""
Talk/Monologue 공통 유틸리티 함수
- 여러 라우터에서 사용하는 공통 함수들
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from routers.talk_policy import moderate_text
from util.utils import get_prompt


OUTPUT_LIMIT = 150

# 정책 가이드 기본 템플릿 (DB에 없을 때 fallback)
_DEFAULT_POLICY_GUIDE = """[정책 안내]
관람객이 민감한 주제({category})를 언급했습니다.

가이드라인:
{fallback_message}

규칙:
- 위 가이드라인의 핵심을 사노의 말투로 자연스럽게 전달
- 딱딱한 안내문이 아닌, 대화하듯 부드럽게
- 전달 후 전시/감정 관련 주제로 자연스럽게 전환
- "I'm sorry", "죄송", "미안" 같은 사과 표현 금지
- "할 수 없어", "다룰 수 없어" 같은 거부 표현 금지"""


def get_policy_guide(db: Session, text_for_check: str) -> tuple[Optional[str], Optional[str]]:
    """
    정책 매칭 시 LLM 프롬프트에 주입할 가이드 텍스트 반환.

    Returns:
        (guide_text, category) 또는 (None, None)
    """
    hit = moderate_text(db, text_for_check)
    if not hit:
        return None, None

    rule, _kw = hit

    # DB에서 템플릿 로드 (없으면 기본값)
    template = get_prompt(db, "policy_guide_prompt", _DEFAULT_POLICY_GUIDE)

    # 템플릿에 값 주입
    try:
        guide = template.format(
            category=rule.category,
            fallback_message=rule.fallback_message,
        )
    except KeyError:
        # 템플릿 형식 오류 시 기본값 사용
        guide = _DEFAULT_POLICY_GUIDE.format(
            category=rule.category,
            fallback_message=rule.fallback_message,
        )

    return guide, rule.category


def apply_policy_guard(db: Session, text_for_check: str, user_text: str = ""):
    """
    정책 필터 적용 (하드 차단용 - 현재는 사용 안 함)
    모든 정책 케이스는 get_policy_guide()로 LLM에 가이드 주입하여 처리.

    return: None (항상)
    """
    # 하드 차단 비활성화 - 모든 케이스를 LLM이 자연스럽게 처리
    return None