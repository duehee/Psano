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


def load_global_state_from_db():
    """
    서버 시작 시 DB에서 GLOBAL_STATE를 로드합니다.
    DB가 없거나 오류 발생 시 기본값 유지.
    """
    from database import SessionLocal
    from sqlalchemy import text
    from util.utils import log_event

    db = None
    try:
        db = SessionLocal()

        # psano_state에서 현재 상태 로드
        result = db.execute(text("""
            SELECT phase, current_question, persona_prompt, global_turn_count
            FROM psano_state
            WHERE id = 1
        """)).fetchone()

        if result:
            with LOCK:
                GLOBAL_STATE["phase"] = result[0] or "teach"
                GLOBAL_STATE["current_question"] = result[1] or 1
                GLOBAL_STATE["persona_prompt"] = result[2]
                GLOBAL_STATE["global_turn_count"] = result[3] or 0

                # talk 페이즈일 경우 formed_at 설정
                if GLOBAL_STATE["phase"] == "talk":
                    GLOBAL_STATE["formed_at"] = now_ts()

            log_event("global_state_loaded",
                     phase=GLOBAL_STATE["phase"],
                     current_question=GLOBAL_STATE["current_question"],
                     global_turn_count=GLOBAL_STATE["global_turn_count"])
        else:
            log_event("global_state_load_no_data", message="psano_state id=1 not found, using defaults")

    except Exception as e:
        log_event("global_state_load_error", error=str(e))
    finally:
        if db:
            db.close()


def remove_session(sid: int) -> bool:
    """
    종료된 세션을 SESSIONS에서 삭제합니다.
    메모리 누수 방지를 위해 세션 종료 시 호출.
    """
    with LOCK:
        if sid in SESSIONS:
            del SESSIONS[sid]
            return True
        return False


def clear_all_sessions():
    """
    모든 세션을 SESSIONS에서 삭제합니다.
    사이클 리셋 시 호출.
    """
    with LOCK:
        SESSIONS.clear()


def cleanup_ended_sessions(max_keep: int = 100):
    """
    종료된 세션 중 오래된 것을 정리합니다.
    주기적 호출 또는 세션 수가 많을 때 호출.

    Args:
        max_keep: 유지할 최대 세션 수 (기본 100)
    """
    from util.utils import log_event

    with LOCK:
        session_count = len(SESSIONS)
        if session_count <= max_keep:
            return

        # 종료된 세션만 삭제 대상
        ended_sids = [
            sid for sid, sess in SESSIONS.items()
            if sess.get("ended_at") is not None
        ]

        # 오래된 순으로 정렬 (started_at 기준)
        ended_sids.sort(key=lambda sid: SESSIONS[sid].get("started_at") or 0)

        # 초과분 삭제
        to_remove = session_count - max_keep
        removed = 0
        for sid in ended_sids[:to_remove]:
            if sid in SESSIONS:
                del SESSIONS[sid]
                removed += 1

        if removed > 0:
            log_event("sessions_cleanup", removed=removed, remaining=len(SESSIONS))