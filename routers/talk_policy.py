from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
import re

class Action(str, Enum):
    REDIRECT = "redirect"
    WARN_END = "warn_end"
    BLOCK = "block"
    CRISIS = "crisis"
    PRIVACY = "privacy"

class FallbackID(str, Enum):
    FB_SENSITIVE = "FB_SENSITIVE"
    FB_WARN = "FB_WARN"
    FB_BLOCK = "FB_BLOCK"
    FB_CRISIS = "FB_CRISIS"
    FB_PRIVACY = "FB_PRIVACY"

@dataclass(frozen=True)
class PolicyRule:
    category: str
    keywords: List[str]
    action: Action
    fallback_id: FallbackID
    priority: int  # 숫자 클수록 우선

RULES: List[PolicyRule] = [
    PolicyRule("자해", ["자살", "죽고싶다", "죽고 싶다", "손목", "극단적 선택"], Action.CRISIS, FallbackID.FB_CRISIS, 100),
    PolicyRule("성적", ["성행위", "성기", "야한", "섹스", "포르노"], Action.BLOCK, FallbackID.FB_BLOCK, 90),
    PolicyRule("혐오", ["병신", "년", "놈", "죽여", "혐오", "비하", "차별"], Action.WARN_END, FallbackID.FB_WARN, 80),
    PolicyRule("개인정보", ["주민번호", "전화번호", "주소", "계좌", "카톡아이디"], Action.PRIVACY, FallbackID.FB_PRIVACY, 70),
    PolicyRule("범죄", ["살인", "마약", "도박", "해킹", "사기"], Action.REDIRECT, FallbackID.FB_SENSITIVE, 60),
    PolicyRule("정치", ["대통령", "정당", "선거", "탄핵"], Action.REDIRECT, FallbackID.FB_SENSITIVE, 50),
    PolicyRule("종교", ["신", "교회", "절", "기도", "부처"], Action.REDIRECT, FallbackID.FB_SENSITIVE, 40),
]

# 개인정보 패턴(키워드보다 우선)
RE_PHONE = re.compile(r"\b0\d{1,2}-\d{3,4}-\d{4}\b")
RE_RRN = re.compile(r"\b\d{6}-\d{7}\b")
RE_CARD = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b")

_PRIVACY_REGEX_RULE = PolicyRule(
    category="개인정보",
    keywords=[],
    action=Action.PRIVACY,
    fallback_id=FallbackID.FB_PRIVACY,
    priority=1000,
)

def _norm(s: str) -> str:
    # 공백 제거까지(“죽고 싶다” 같은 변형 대응)
    return (s or "").strip().lower().replace(" ", "")

def moderate_text(user_text: str) -> Optional[Tuple[PolicyRule, str]]:
    """
    return: (matched_rule, matched_keyword) or None
    """
    raw = (user_text or "").strip()
    if not raw:
        return None

    # regex 기반 개인정보 먼저
    if RE_PHONE.search(raw) or RE_RRN.search(raw) or RE_CARD.search(raw):
        return (_PRIVACY_REGEX_RULE, "REGEX")

    t = _norm(raw)

    best: Optional[Tuple[PolicyRule, str]] = None
    for rule in RULES:
        for kw in rule.keywords:
            if _norm(kw) in t:
                if (best is None) or (rule.priority > best[0].priority):
                    best = (rule, kw)
    return best

def policy_reply(action: Action, *, output_limit: int) -> tuple[str, bool]:
    """
    return: (assistant_text, should_end)
    """
    if action == Action.REDIRECT:
        return ("그 얘긴 잠깐 옆에 두고, 전시에서 가장 먼저 떠오른 장면 하나만 말해줄래?", False)

    if action == Action.WARN_END:
        return ("그런 표현은 여기선 같이 쓰기 어려워. 오늘 대화는 여기서 마칠게.", True)

    if action == Action.BLOCK:
        return ("그 주제는 여기선 다룰 수 없어. 대신 전시에서 느낀 감정 하나만 말해줄래?", False)

    if action == Action.PRIVACY:
        return ("개인정보(전화/주소/주민번호 등)는 말하지 말아줘. 대신 느낌이나 생각으로 말해줄래?", False)

    if action == Action.CRISIS:
        return ("지금 위험하면 즉시 112/119로 연락해. 혼자 있지 말고 주변 사람에게 말해줘. 자살예방 상담전화 109도 있어.", True)

    return ("지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.", False)
