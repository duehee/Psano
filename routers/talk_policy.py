from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import re
import time

from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI

client = OpenAI()

class Action(str, Enum):
    REDIRECT = "redirect"
    WARN_END = "warn_end"
    BLOCK = "block"
    CRISIS = "crisis"
    PRIVACY = "privacy"


@dataclass
class PolicyRule:
    id: int
    category: str
    keywords: List[str]
    is_regex: bool
    action: Action
    priority: int
    fallback_message: str
    should_end: bool


# 캐시 (60초 TTL)
_rules_cache: List[PolicyRule] = []
_cache_time: float = 0
CACHE_TTL = 60


def _load_rules(db: Session) -> List[PolicyRule]:
    """DB에서 정책 규칙 로드 (캐시 적용)"""
    global _rules_cache, _cache_time

    if _rules_cache and (time.time() - _cache_time < CACHE_TTL):
        return _rules_cache

    rows = db.execute(
        text("""
            SELECT id, category, keywords, is_regex, action, priority,
                   fallback_message, should_end
            FROM psano_policy_rules
            WHERE enabled = TRUE
            ORDER BY priority DESC
        """)
    ).mappings().all()

    rules = []
    for row in rows:
        keywords_raw = (row.get("keywords") or "").strip()
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

        try:
            action = Action(row.get("action", "redirect"))
        except ValueError:
            action = Action.REDIRECT

        rules.append(PolicyRule(
            id=int(row.get("id", 0)),
            category=row.get("category", ""),
            keywords=keywords,
            is_regex=bool(row.get("is_regex", False)),
            action=action,
            priority=int(row.get("priority", 50)),
            fallback_message=row.get("fallback_message", ""),
            should_end=bool(row.get("should_end", False)),
        ))

    _rules_cache = rules
    _cache_time = time.time()
    return rules


def _norm(s: str) -> str:
    """공백 제거 + 소문자화"""
    return (s or "").strip().lower().replace(" ", "")


def moderate_text(db: Session, user_text: str) -> Optional[Tuple[PolicyRule, str]]:
    """
    사용자 텍스트를 정책 규칙에 따라 검사.
    return: (matched_rule, matched_keyword) or None
    """
    raw = (user_text or "").strip()
    if not raw:
        return None

    rules = _load_rules(db)
    normalized = _norm(raw)

    best: Optional[Tuple[PolicyRule, str]] = None

    for rule in rules:
        if rule.is_regex:
            # 정규식 모드: keywords[0]을 전체 패턴으로 사용
            pattern = rule.keywords[0] if rule.keywords else ""
            if pattern:
                try:
                    if re.search(pattern, raw, re.IGNORECASE):
                        if (best is None) or (rule.priority > best[0].priority):
                            best = (rule, "REGEX")
                except re.error:
                    pass
        else:
            # 키워드 모드
            for kw in rule.keywords:
                if _norm(kw) in normalized:
                    if (best is None) or (rule.priority > best[0].priority):
                        best = (rule, kw)
                    break  # 이 규칙에서 매칭됐으면 다음 규칙으로

    return best


def generate_policy_response(
    db: Session,
    rule: PolicyRule,
    user_text: str,
    *,
    use_gpt: bool = True,
) -> Tuple[str, bool]:
    """
    정책에 맞는 응답 생성.
    fallback_message를 가이드로 GPT가 사노 스타일로 생성.

    return: (response_text, should_end)
    """
    if not use_gpt:
        return (rule.fallback_message, rule.should_end)

    # 성장단계 로드 (스타일 반영용)
    stage_row = db.execute(
        text("""
            SELECT stage_name_kr FROM psano_growth_stages
            WHERE (SELECT GREATEST(0, current_question - 1) FROM psano_state WHERE id = 1)
                  BETWEEN min_answers AND max_answers
            ORDER BY stage_id ASC LIMIT 1
        """)
    ).mappings().first()
    stage_name = stage_row.get("stage_name_kr") if stage_row else "태동기"

    prompt = f"""너는 전시 작품 '사노'야. 관람객이 민감한 주제를 언급했어.

[성장단계: {stage_name}]
[정책 카테고리: {rule.category}]
[대화 종료 여부: {'종료' if rule.should_end else '계속'}]

관람객 메시지: {user_text[:100]}

가이드라인:
{rule.fallback_message}

규칙:
- 위 가이드라인의 핵심 내용을 전달하되, 사노의 말투로 자연스럽게 변환
- 한국어, 2~3문장 이내
- 딱딱한 안내문이 아니라 사노가 직접 말하는 느낌으로
- {'대화를 마무리하는 느낌으로' if rule.should_end else '부드럽게 전환하는 느낌으로'}

사노의 응답:"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        response_text = (resp.choices[0].message.content or "").strip()
        if response_text:
            return (response_text[:200], rule.should_end)
    except Exception:
        pass

    # fallback
    return (rule.fallback_message, rule.should_end)


def clear_cache():
    """캐시 강제 초기화 (테스트/관리용)"""
    global _rules_cache, _cache_time
    _rules_cache = []
    _cache_time = 0