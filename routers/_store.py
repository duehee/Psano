from __future__ import annotations

import time
from threading import RLock
from typing import Dict, Any

LOCK = RLock()

# 전역 상태(= psano_state 흉내) - 메모리 캐시용
GLOBAL_STATE: Dict[str, Any] = {
    "phase": "teach",              # teach / talk
    "current_question": 1,         # 1~365
    "formed_at": None,             # timestamp(float) or None
    "persona_prompt": None,        # str or None
    "values_summary": None,        # dict/json or None
    "allow_talk_in_teach": True,
    "global_turn_count": 0,        # 글로벌 턴 카운트 (대화기)
    "cycle_number": 1,             # 현재 사이클 번호
}

# 세션 저장소 - 메모리 캐시용 (DB가 primary)
SESSIONS: Dict[int, Dict[str, Any]] = {}


def now_ts() -> float:
    return time.time()