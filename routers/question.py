from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.question import QuestionResponse
from utils import get_config

router = APIRouter()

# 하드코딩 fallback (DB 없을 때)
_DEFAULT_SESSION_LIMIT = 5
_DEFAULT_MAX_QUESTIONS = 380

@router.get("/current", response_model=QuestionResponse)
def get_current_question(
    session_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    # 설정 로드
    session_limit = get_config(db, "session_question_limit", _DEFAULT_SESSION_LIMIT)
    max_questions = get_config(db, "max_questions", _DEFAULT_MAX_QUESTIONS)

    # 0) 세션 유효성 + start_question_id 조회
    ses = db.execute(
        text("""
            SELECT id, ended_at, start_question_id
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": int(session_id)}
    ).mappings().first()

    if not ses:
        raise HTTPException(status_code=404, detail=f"session not found: {session_id}")

    if ses["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    start_question_id = int(ses.get("start_question_id") or 1)

    # 1) phase 확인
    st = db.execute(
        text("""
            SELECT phase
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    if st["phase"] != "teach":
        raise HTTPException(status_code=409, detail="phase is not teach")

    # 2) session_question_index 계산 (답변 기준)
    answered_cnt = db.execute(
        text("""
            SELECT COUNT(*) AS cnt
            FROM answers
            WHERE session_id = :sid
        """),
        {"sid": int(session_id)}
    ).mappings().first()

    answered_cnt = int(answered_cnt["cnt"]) if answered_cnt else 0
    session_question_index = answered_cnt + 1  # 1~5

    if session_question_index > session_limit:
        raise HTTPException(status_code=409, detail="session question limit reached")

    # 3) 세션별 질문 ID 계산: start_question_id + 답변 수
    qid = start_question_id + answered_cnt

    if qid > max_questions:
        raise HTTPException(status_code=409, detail="teach phase already completed")

    # 4) 질문 조회
    q = db.execute(
        text("""
            SELECT id, axis_key, question_text, choice_a, choice_b, enabled, value_a_key, value_b_key
            FROM questions
            WHERE id = :qid
        """),
        {"qid": qid}
    ).mappings().first()

    if not q:
        raise HTTPException(status_code=404, detail=f"question not found: {qid}")

    # disabled면 다음 enabled 질문 찾기
    if not bool(q["enabled"]):
        next_q = db.execute(
            text("""
                SELECT id, axis_key, question_text, choice_a, choice_b, enabled, value_a_key, value_b_key
                FROM questions
                WHERE id > :qid AND enabled = 1
                ORDER BY id ASC
                LIMIT 1
            """),
            {"qid": qid}
        ).mappings().first()

        if not next_q:
            raise HTTPException(status_code=409, detail="no enabled question available")

        q = next_q

    # 5) 응답
    return {
        "id": int(q["id"]),
        "axis_key": q["axis_key"],
        "question_text": q["question_text"],
        "choice_a": q["choice_a"],
        "choice_b": q["choice_b"],
        "enabled": bool(q["enabled"]),
        "value_a_key": q.get("value_a_key"),
        "value_b_key": q.get("value_b_key"),
        "session_question_index": int(session_question_index),
    }
