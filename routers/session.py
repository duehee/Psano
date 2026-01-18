from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from schemas.session import (
    SessionStartRequest, SessionStartResponse,
    SessionEndRequest, SessionEndResponse
)
from routers._store import LOCK, GLOBAL_STATE, SESSIONS, now_ts
from database import get_db

router = APIRouter()

KST = ZoneInfo("Asia/Seoul")


def now_kst_naive() -> datetime:
    # DB DATETIME에 그대로 박을 "한국 시간" (tz 없는 naive datetime)
    return datetime.utcnow() + timedelta(hours=9)

def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)

def _epoch_to_kst_iso(ts):
    if ts is None:
        return None

    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc).astimezone(KST)
    dt = dt.replace(tzinfo=None)  # KST naive로 표기
    return _iso(dt)

@router.post("/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    name = (req.visitor_name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="visitor_name is empty")

    try:
        started_at = now_kst_naive()  # ✅ +9
        result = db.execute(
            text("""
                INSERT INTO sessions (visitor_name, started_at)
                VALUES (:visitor_name, :started_at)
            """),
            {"visitor_name": name, "started_at": started_at},
        )
        db.commit()

        sid = int(getattr(result, "lastrowid", 0) or 0)
        if sid <= 0:
            sid = int(db.execute(text("SELECT LAST_INSERT_ID()")).scalar() or 0)
        if sid <= 0:
            raise RuntimeError("failed to allocate session id")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    with LOCK:
        SESSIONS[sid] = {
            "id": sid,
            "visitor_name": name,
            "started_at": started_at,  # 이건 epoch라서 상관없음(원하면 이것도 KST로 바꿀 수 있음)
            "ended_at": None,
            "end_reason": None,
        }

        return {
            "session_id": sid,
            "phase": GLOBAL_STATE["phase"],
            "current_question": int(GLOBAL_STATE["current_question"]),
        }

@router.post("/end", response_model=SessionEndResponse)
def end_session(req: SessionEndRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)

    try:
        ended_at = now_kst_naive()  # ✅ +9

        try:
            res = db.execute(
                text("""
                    UPDATE sessions
                    SET ended_at = :ended_at,
                        end_reason = :end_reason
                    WHERE id = :id
                """),
                {"ended_at": ended_at, "end_reason": req.reason, "id": sid},
            )
        except Exception:
            res = db.execute(
                text("""
                    UPDATE sessions
                    SET ended_at = :ended_at
                    WHERE id = :id
                """),
                {"ended_at": ended_at, "id": sid},
            )

        db.commit()

        if (getattr(res, "rowcount", 0) or 0) == 0:
            raise HTTPException(status_code=404, detail="session not found")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    with LOCK:
        sess = SESSIONS.get(sid)
        if sess and sess.get("ended_at") is None:
            sess["ended_at"] = ended_at  # ✅ now_ts() 대신 KST naive datetime
            sess["end_reason"] = req.reason

    return {"session_id": sid, "ended": True}

@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    sid = int(session_id)

    # 1) 메모리 캐시 우선
    with LOCK:
        sess = SESSIONS.get(sid)
        if sess:
            started = _iso(sess.get("started_at"))
            ended = _iso(sess.get("ended_at"))
            return {
                "session_id": sid,
                "visitor_name": sess.get("visitor_name"),
                "started_at": started,
                "ended_at": ended,
                "end_reason": sess.get("end_reason")
            }

    # 2) DB fallback
    row = db.execute(
        text("""
            SELECT id, visitor_name, started_at, ended_at, end_reason
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": sid}
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="session not found")

    ended_at = row.get("ended_at")
    return {
        "session_id": int(row["id"]),
        "visitor_name": row["visitor_name"],
        "started_at": _iso(row["started_at"]),                 # ✅
        "ended_at": _iso(ended_at) if ended_at else None,      # ✅
        "end_reason": row.get("end_reason")
    }