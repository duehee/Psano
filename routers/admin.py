from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.admin import (
    AdminSessionsResponse, AdminProgressResponse,
    AdminResetRequest, AdminResetResponse,
    AdminPhaseSetRequest, AdminPhaseSetResponse,
    AdminSetCurrentQuestionRequest, AdminSetCurrentQuestionResponse,
)

router = APIRouter()

MAX_QUESTIONS = 380

def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)

def ensure_psano_state_row(db: Session):
    """
    psano_state에 id=1 row 없으면 만들어 둠.
    ⚠️ 여기선 commit 안 함(호출한 endpoint에서 commit/rollback 관리)
    """
    row = db.execute(text("SELECT id FROM psano_state WHERE id=1")).mappings().first()
    if row:
        return

    db.execute(
        text("""
            INSERT INTO psano_state (id, phase, current_question)
            VALUES (1, 'formation', 1)
        """)
    )

def now_kst():
    # DB에 "그냥 KST로 박겠다"면 이걸로 넣으면 됨
    return datetime.utcnow() + timedelta(hours=9)

@router.get("/sessions", response_model=AdminSessionsResponse)
def list_sessions(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    total_row = db.execute(text("SELECT COUNT(*) AS cnt FROM sessions")).mappings().first()
    total = int(total_row["cnt"]) if total_row else 0

    # end_reason 컬럼이 있을 수도/없을 수도 있으니 fallback 쿼리
    try:
        rows = db.execute(
            text("""
                SELECT id, visitor_name, started_at, ended_at, end_reason
                FROM sessions
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        ).mappings().all()

        sessions = []
        for r in rows:
            sessions.append({
                "id": int(r["id"]),
                "visitor_name": r["visitor_name"],
                "started_at": _iso(r["started_at"]),
                "ended_at": _iso(r["ended_at"]),
                "end_reason": r.get("end_reason"),
            })

    except Exception:
        rows = db.execute(
            text("""
                SELECT id, visitor_name, started_at, ended_at
                FROM sessions
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        ).mappings().all()

        sessions = []
        for r in rows:
            sessions.append({
                "id": int(r["id"]),
                "visitor_name": r["visitor_name"],
                "started_at": _iso(r["started_at"]),
                "ended_at": _iso(r["ended_at"]),
                "end_reason": None,
            })

    return {"total": total, "sessions": sessions}

@router.get("/progress", response_model=AdminProgressResponse)
def get_progress(db: Session = Depends(get_db)):
    st = db.execute(
        text("""
            SELECT phase, current_question
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    phase = st["phase"]
    if phase not in ("formation", "chat"):
        phase = "formation"

    current_q = int(st["current_question"])

    if phase == "formation":
        answered = max(0, min(MAX_QUESTIONS, current_q - 1))
    else:
        answered = MAX_QUESTIONS

    ratio = 0.0 if MAX_QUESTIONS <= 0 else float(answered) / float(MAX_QUESTIONS)

    return {
        "phase": phase,
        "current_question": current_q,
        "answered_count": answered,
        "max_questions": MAX_QUESTIONS,
        "progress_ratio": ratio,
    }

@router.post("/reset", response_model=AdminResetResponse)
def admin_reset(req: AdminResetRequest, db: Session = Depends(get_db)):
    """
    - 기본: reset_state만 True (formation + 1번 질문으로)
    - reset_answers: answers 전체 삭제
    - reset_sessions: sessions 전체 삭제
    """
    try:
        ensure_psano_state_row(db)

        if req.reset_answers:
            db.execute(text("DELETE FROM answers"))

        if req.reset_sessions:
            db.execute(text("DELETE FROM sessions"))

        if req.reset_state:
            # 컬럼이 있을 수도/없을 수도 있으니 안전하게 처리
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'formation',
                            current_question = 1,
                            formed_at = NULL,
                            persona_prompt = NULL,
                            values_summary = NULL
                        WHERE id = 1
                    """)
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'formation',
                            current_question = 1
                        WHERE id = 1
                    """)
                )

        db.commit()
        return AdminResetResponse(
            ok=True,
            reset_answers=req.reset_answers,
            reset_sessions=req.reset_sessions,
            reset_state=req.reset_state,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

@router.post("/phase/set", response_model=AdminPhaseSetResponse)
def admin_set_phase(req: AdminPhaseSetRequest, db: Session = Depends(get_db)):
    """
    테스트용 phase 강제 변경.
    - formation: formed_at NULL 처리(가능하면)
    - chat: formed_at 현재시간 기록(가능하면)
    """
    if req.phase not in ("formation", "chat"):
        raise HTTPException(status_code=400, detail="invalid phase")

    try:
        ensure_psano_state_row(db)

        if req.phase == "formation":
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'formation',
                            formed_at = NULL
                        WHERE id = 1
                    """)
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'formation'
                        WHERE id = 1
                    """)
                )
        else:
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'chat',
                            formed_at = :formed_at
                        WHERE id = 1
                    """),
                    {"formed_at": now_kst()},
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'chat'
                        WHERE id = 1
                    """)
                )

        db.commit()
        return AdminPhaseSetResponse(ok=True, phase=req.phase)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")


@router.post("/state/set_current_question", response_model=AdminSetCurrentQuestionResponse)
def admin_set_current_question(req: AdminSetCurrentQuestionRequest, db: Session = Depends(get_db)):
    """
    테스트용 현재 질문 강제 설정.
    """
    try:
        ensure_psano_state_row(db)

        db.execute(
            text("""
                UPDATE psano_state
                SET current_question = :q
                WHERE id = 1
            """),
            {"q": int(req.current_question)},
        )
        db.commit()

        return AdminSetCurrentQuestionResponse(ok=True, current_question=int(req.current_question))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")