import time

from __future__ import annotations
from threading import RLock
from typing import Dict, Any

LOCK = RLock()

# 전역 상태(= psano_state 흉내)
GLOBAL_STATE: Dict[str, Any] = {
    "phase": "formation",          # formation / chat
    "current_question": 1,         # 1~380
    "formed_at": None,             # timestamp(float) or None
    "persona_prompt": None,        # str or None
    "values_summary": None,        # dict/json or None
    "allow_talk_in_formation": True,
}

# 세션 저장소
SESSION_SEQ = 0
SESSIONS: Dict[int, Dict[str, Any]] = {}

# answers 저장소(나중에 DB answers로 대체)
ANSWERS = []  # list[dict]: {session_id, question_id, choice, created_at}

# 질문 임시 저장소(나중에 DB questions로 대체)
# 여기선 최소 예시만 넣어둠. 실제 380개는 디자이너 파일로 seed할 예정.
QUESTIONS: Dict[int, Dict[str, Any]] = {
    1: {
        "id": 1,
        "axis_key": "freedom",
        "question_text": "너는 더 자유로운 선택을 원하니, 아니면 질서 있는 기준을 원하니?",
        "choice_a": "자유가 좋아.",
        "choice_b": "기준이 좋아.",
        "enabled": True,
    }
}

MAX_QUESTIONS = 380


def now_ts() -> float:
    return time.time()


def next_session_id() -> int:
    global SESSION_SEQ
    SESSION_SEQ += 1
    return SESSION_SEQ


def ensure_question_exists(qid: int) -> Dict[str, Any]:
    q = QUESTIONS.get(qid)
    if not q or not q.get("enabled", True):
        raise KeyError(f"question not found or disabled: {qid}")
    return q


def is_formation_done() -> bool:
    return GLOBAL_STATE["current_question"] > MAX_QUESTIONS