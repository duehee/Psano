from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from routers._store import LOCK, SESSIONS


def now_kst_naive() -> datetime:
    # DB DATETIME에 그대로 박을 "한국 시간"(tz 없는 naive)
    return datetime.utcnow() + timedelta(hours=9)


def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)


def end_session_core(db: Session, sid: int, reason: str) -> Dict[str, Any]:
    """
    sessions.ended_at / end_reason을 갱신하고, 멱등 처리까지 수행.
    - 이미 종료된 세션이면 already_ended=True로 그대로 반환
    - 성공 종료면 already_ended=False
    - 메모리 캐시(SESSIONS)도 같이 반영
    """
    sid = int(sid)
    reason = (reason or "completed")

    # 0) 세션 존재/현재 종료 상태 확인(멱등)
    row = db.execute(
        text("""
            SELECT id, ended_at, end_reason
            FROM sessions
            WHERE id = :id
        """),
        {"id": sid},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="session not found")

    if row.get("ended_at") is not None:
        ended_at = row.get("ended_at")
        ended_iso = _iso(ended_at) if ended_at else None

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

        # 2) rowcount==0이면 이미 종료됐을 가능성 → 재조회해서 반환
        if (getattr(res, "rowcount", 0) or 0) == 0:
            row2 = db.execute(
                text("""
                    SELECT ended_at, end_reason
                    FROM sessions
                    WHERE id = :id
                """),
                {"id": sid},
            ).mappings().first()

            ended_iso = _iso(row2.get("ended_at")) if row2 else None
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
        "ended_at": _iso(ended_at),
    }
