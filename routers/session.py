from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from services.session_service import end_session_core

from schemas.session import (
    SessionStartRequest, SessionStartResponse,
    SessionEndRequest, SessionEndResponse
)
from routers._store import LOCK, GLOBAL_STATE, SESSIONS
from database import get_db
from utils import now_kst_naive, iso

router = APIRouter()


def _read_session_row(db: Session, sid: int):
    """sessions 테이블에서 세션 정보 조회"""
    return db.execute(
        text("""
            SELECT id, visitor_name, started_at, ended_at, end_reason,
                   topic_id, talk_memory, turn_count, start_question_id
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": sid}
    ).mappings().first()


@router.post("/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    name = (req.visitor_name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="visitor_name is empty")

    try:
        started_at = now_kst_naive()  # KST +9

        # 현재 질문 번호 조회 (teach phase용 start_question_id)
        st = db.execute(
            text("SELECT current_question FROM psano_state WHERE id = 1")
        ).mappings().first()
        start_question_id = int(st["current_question"]) if st else 1

        # teach/talk 여부와 상관없이 "세션 기본 정보만" 생성
        # start_question_id: 타임아웃 시 롤백용
        result = db.execute(
            text("""
                INSERT INTO sessions (visitor_name, started_at, start_question_id)
                VALUES (:visitor_name, :started_at, :start_question_id)
            """),
            {"visitor_name": name, "started_at": started_at, "start_question_id": start_question_id},
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
            "started_at": started_at,   # datetime
            "ended_at": None,
            "end_reason": None,
            "start_question_id": start_question_id,  # 타임아웃 롤백용
            # talk 전용은 "아직 시작 안 함" 상태로 둠
            "topic_id": None,
            "talk_memory": None,
            "turn_count": 0,
        }

        return {
            "session_id": sid,
            "phase": GLOBAL_STATE["phase"],
            "current_question": start_question_id,
        }


@router.post("/end", response_model=SessionEndResponse)
def end_session(req: SessionEndRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    reason = (req.reason or "completed")
    return end_session_core(db, sid, reason)

@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    sid = int(session_id)

    # 1) 메모리 캐시 우선
    with LOCK:
        sess = SESSIONS.get(sid)
        if sess:
            return {
                "session_id": sid,
                "visitor_name": sess.get("visitor_name"),
                "started_at": iso(sess.get("started_at")),
                "ended_at": iso(sess.get("ended_at")),
                "end_reason": sess.get("end_reason"),
                # talk 전용(없으면 None/0)
                "topic_id": sess.get("topic_id"),
                "talk_memory": sess.get("talk_memory"),
                "turn_count": sess.get("turn_count", 0),
            }

    # 2) DB fallback (optional 컬럼 안전)
    row = _read_session_row(db, sid)
    if not row:
        raise HTTPException(status_code=404, detail="session not found")

    ended_at = row.get("ended_at")
    return {
        "session_id": int(row["id"]),
        "visitor_name": row.get("visitor_name"),
        "started_at": iso(row.get("started_at")),
        "ended_at": iso(ended_at) if ended_at else None,
        "end_reason": row.get("end_reason"),
        "topic_id": row.get("topic_id"),
        "talk_memory": row.get("talk_memory"),
        "turn_count": int(row.get("turn_count") or 0),
    }
