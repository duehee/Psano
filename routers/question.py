from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.question import QuestionResponse

router = APIRouter()

SESSION_QUESTION_LIMIT = 5
MAX_QUESTIONS = 380  # 기존 로직 유지

@router.get("/current", response_model=QuestionResponse)
def get_current_question(
    session_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    # 0) 세션 유효성
    ses = db.execute(
        text("""
            SELECT id, ended_at
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": int(session_id)}
    ).mappings().first()

    if not ses:
        raise HTTPException(status_code=404, detail=f"session not found: {session_id}")

    if ses["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 1) phase / current_question
    st = db.execute(
        text("""
            SELECT phase, current_question
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    if st["phase"] != "teach":
        raise HTTPException(status_code=409, detail="phase is not teach")

    # 2) session_question_index 계산(답변 기준)
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

    if session_question_index > SESSION_QUESTION_LIMIT:
        raise HTTPException(status_code=409, detail="session question limit reached")

    qid = int(st["current_question"])
    if qid > MAX_QUESTIONS:
        raise HTTPException(status_code=409, detail="teach phase already completed")

    # 3) value_a_key/value_b_key까지 같이 조회 (여기가 핵심 수정)
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

    # disabled면 다음 enabled 스킵
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

        db.execute(
            text("""
                UPDATE psano_state
                SET current_question = :new_qid
                WHERE id = 1
            """),
            {"new_qid": int(next_q["id"])},
        )
        db.commit()

        q = next_q

    # 4) 응답에 value 키도 내려주기
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
