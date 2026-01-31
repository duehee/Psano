from __future__ import annotations

import re
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
from util.utils import now_kst_naive, iso

router = APIRouter()

# 닉네임 검증: 한글, 영문, 숫자만 허용 (공백, 이모지, 특수문자 불가)
VISITOR_NAME_PATTERN = re.compile(r'^[가-힣a-zA-Z0-9]+$')
VISITOR_NAME_MAX_LEN = 12


def _validate_visitor_name(name: str | None) -> str:
    """
    닉네임 검증 및 정규화.
    - 빈 값이면 '관람객' 반환
    - 한글/영문/숫자만 허용
    - 최대 12자
    """
    if not name:
        return "관람객"

    name = name.strip()
    if not name:
        return "관람객"

    # 길이 체크
    if len(name) > VISITOR_NAME_MAX_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"닉네임은 {VISITOR_NAME_MAX_LEN}자 이하여야 합니다"
        )

    # 패턴 체크 (한글/영문/숫자만)
    if not VISITOR_NAME_PATTERN.match(name):
        raise HTTPException(
            status_code=400,
            detail="닉네임은 한글, 영문, 숫자만 사용할 수 있습니다 (공백/특수문자/이모지 불가)"
        )

    return name


def _read_session_row(db: Session, sid: int):
    """sessions 테이블에서 세션 정보 조회"""
    return db.execute(
        text("""
            SELECT id, visitor_name, started_at, ended_at, end_reason,
                   idle_id, idle_talk_memory, idle_turn_count, start_question_id
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": sid}
    ).mappings().first()


def _start_session_core(db: Session, visitor_name: str | None):
    """세션 시작 핵심 로직"""
    name = _validate_visitor_name(visitor_name)

    try:
        started_at = now_kst_naive()  # KST +9

        # 현재 질문 번호 조회 (teach phase용 start_question_id)
        st = db.execute(
            text("SELECT current_question FROM psano_state WHERE id = 1")
        ).mappings().first()
        start_question_id = int(st["current_question"]) if st else 1

        # teach/talk 여부와 상관없이 "세션 기본 정보만" 생성
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
            "started_at": started_at,
            "ended_at": None,
            "end_reason": None,
            "start_question_id": start_question_id,
            "idle_id": None,
            "idle_talk_memory": None,
            "idle_turn_count": 0,
        }

    # 이벤트 로깅
    from util.utils import log_event
    log_event("session_start", session_id=sid, visitor=name, start_question=start_question_id)

    return {
        "session_id": sid,
        "phase": GLOBAL_STATE["phase"],
        "current_question": start_question_id,
    }


@router.post("/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest, db: Session = Depends(get_db)):
    return _start_session_core(db, req.visitor_name)


@router.get("/start", response_model=SessionStartResponse)
def start_session_get(visitor_name: str | None = None, db: Session = Depends(get_db)):
    """TD용 GET 엔드포인트 - Query 파라미터로 세션 시작"""
    return _start_session_core(db, visitor_name)


@router.post("/end", response_model=SessionEndResponse)
def end_session(req: SessionEndRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    reason = (req.reason or "completed")
    return end_session_core(db, sid, reason)


@router.get("/end", response_model=SessionEndResponse)
def end_session_get(session_id: int, reason: str = "completed", db: Session = Depends(get_db)):
    """TD용 GET 엔드포인트 - Query 파라미터로 세션 종료"""
    return end_session_core(db, session_id, reason)

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
                "idle_id": sess.get("idle_id"),
                "idle_talk_memory": sess.get("idle_talk_memory"),
                "idle_turn_count": sess.get("idle_turn_count", 0),
            }

    # 2) DB fallback
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
        "idle_id": row.get("idle_id"),
        "idle_talk_memory": row.get("idle_talk_memory"),
        "idle_turn_count": int(row.get("idle_turn_count") or 0),
    }
