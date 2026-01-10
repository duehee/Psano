from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.admin import AdminSessionsResponse, AdminProgressResponse

router = APIRouter()

MAX_QUESTIONS = 380

def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)

@router.get("/sessions", response_model=AdminSessionsResponse)
def list_sessions(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    total_row = db.execute(text("SELECT COUNT(*) AS cnt FROM sessions")).mappings().first()
    total = int(total_row["cnt"]) if total_row else 0

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
            "end_reason": r["end_reason"],
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
    current_q = int(st["current_question"])

    # formation이면 current_question은 "다음 질문 번호"
    if phase == "formation":
        answered = max(0, min(MAX_QUESTIONS, current_q - 1))
    else:
        # chat이면 사실상 형성 완료로 간주
        answered = MAX_QUESTIONS

    ratio = 0.0 if MAX_QUESTIONS <= 0 else float(answered) / float(MAX_QUESTIONS)

    return {
        "phase": phase,
        "current_question": current_q,
        "answered_count": answered,
        "max_questions": MAX_QUESTIONS,
        "progress_ratio": ratio,
    }