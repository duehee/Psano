from __future__ import annotations

from typing import Any, Dict

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from routers._store import LOCK, SESSIONS
from util.utils import now_kst_naive, iso
from util.constants import ALLOWED_VALUE_KEYS, MAX_QUESTIONS


def end_session_core(db: Session, sid: int, reason: str) -> Dict[str, Any]:
    """
    sessions.ended_at / end_reason을 갱신하고, 멱등 처리까지 수행.
    - 이미 종료된 세션이면 already_ended=True로 그대로 반환
    - 정상 종료 (completed): psano_personality 일괄 반영 + current_question 업데이트
    - 타임아웃 (timeout): answers 삭제, current_question은 그대로
    - 메모리 캐시(SESSIONS)도 같이 반영
    """
    sid = int(sid)
    reason = (reason or "completed")

    # 0) 세션 존재/현재 종료 상태 확인(멱등) + start_question_id 조회
    row = db.execute(
        text("""
            SELECT id, ended_at, end_reason, start_question_id
            FROM sessions
            WHERE id = :id
        """),
        {"id": sid},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="session not found")

    start_question_id = int(row.get("start_question_id") or 1)

    if row.get("ended_at") is not None:
        ended_at = row.get("ended_at")
        ended_iso = iso(ended_at) if ended_at else None

        with LOCK:
            sess = SESSIONS.get(sid)
            if sess:
                sess["ended_at"] = ended_at
                sess["end_reason"] = row.get("end_reason")

        return {
            "session_id": sid,
            "ended": True,
            "already_ended": True,
            "end_reason": row.get("end_reason"),
            "ended_at": ended_iso,
        }

    try:
        ended_at = now_kst_naive()  # KST +9

        if reason == "timeout":
            # 타임아웃: answers 삭제, current_question은 그대로
            db.execute(
                text("DELETE FROM answers WHERE session_id = :sid"),
                {"sid": sid}
            )
        else:
            # 정상 종료: psano_personality 일괄 반영 + current_question 업데이트
            # 1) 해당 세션의 answers에서 chosen_value_key 집계
            answers = db.execute(
                text("""
                    SELECT chosen_value_key, COUNT(*) as cnt
                    FROM answers
                    WHERE session_id = :sid
                    GROUP BY chosen_value_key
                """),
                {"sid": sid}
            ).mappings().all()

            # 2) psano_personality 업데이트 (SQL Injection 방지: whitelist 검증)
            for ans in answers:
                col = ans["chosen_value_key"]
                cnt = int(ans["cnt"])
                if col and cnt > 0 and col in ALLOWED_VALUE_KEYS:
                    db.execute(
                        text(f"UPDATE psano_personality SET `{col}` = `{col}` + :cnt WHERE id = 1"),
                        {"cnt": cnt}
                    )

            # 3) current_question 업데이트 (start_question_id + 5 또는 다음 enabled)
            answer_count = db.execute(
                text("SELECT COUNT(*) AS cnt FROM answers WHERE session_id = :sid"),
                {"sid": sid}
            ).mappings().first()
            answered_in_session = int(answer_count["cnt"]) if answer_count else 0

            # 다음 질문 찾기: start_question_id + answered_in_session 이후의 enabled 질문
            next_start = start_question_id + answered_in_session
            next_q = db.execute(
                text("""
                    SELECT id FROM questions
                    WHERE id >= :next_start AND enabled = 1
                    ORDER BY id ASC
                    LIMIT 1
                """),
                {"next_start": next_start}
            ).mappings().first()

            new_current_q = int(next_q["id"]) if next_q else (MAX_QUESTIONS + 1)  # 없으면 형성 완료

            db.execute(
                text("UPDATE psano_state SET current_question = :q WHERE id = 1"),
                {"q": new_current_q}
            )

        # 세션 종료 처리 (ended_at IS NULL 조건으로 race condition 방지)
        res = db.execute(
            text("""
                UPDATE sessions
                SET ended_at = :ended_at, end_reason = :end_reason
                WHERE id = :id AND ended_at IS NULL
            """),
            {"ended_at": ended_at, "end_reason": reason, "id": sid},
        )
        db.commit()

        # rowcount==0이면 이미 종료됐을 가능성 → 재조회해서 반환
        if (getattr(res, "rowcount", 0) or 0) == 0:
            row2 = db.execute(
                text("""
                    SELECT ended_at, end_reason
                    FROM sessions
                    WHERE id = :id
                """),
                {"id": sid},
            ).mappings().first()

            ended_iso = iso(row2.get("ended_at")) if row2 else None
            return {
                "session_id": sid,
                "ended": True,
                "already_ended": True,
                "end_reason": (row2 or {}).get("end_reason"),
                "ended_at": ended_iso,
            }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    # 3) 메모리 캐시 반영
    with LOCK:
        sess = SESSIONS.get(sid)
        if sess and sess.get("ended_at") is None:
            sess["ended_at"] = ended_at
            sess["end_reason"] = reason

    return {
        "session_id": sid,
        "ended": True,
        "already_ended": False,
        "end_reason": reason,
        "ended_at": iso(ended_at),
    }
