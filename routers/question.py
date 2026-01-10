from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.question import QuestionResponse

router = APIRouter()

@router.get("/current", response_model=QuestionResponse)
def get_current_question(db: Session = Depends(get_db)):
    # 1) 현재 phase / current_question 가져오기 (단일 row)
    st = db.execute(
        text("""
            SELECT phase, current_question
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    if st["phase"] != "formation":
        raise HTTPException(status_code=409, detail="phase is not formation")

    qid = int(st["current_question"])
    if qid > 380:
        # formation 완료 상태로 보고 싶으면 409 또는 200+메시지 중 택1
        raise HTTPException(status_code=409, detail="formation already completed")

    # 2) 질문 조회
    q = db.execute(
        text("""
            SELECT id, axis_key, question_text, choice_a, choice_b, enabled
            FROM questions
            WHERE id = :qid
        """),
        {"qid": qid}
    ).mappings().first()

    if not q:
        raise HTTPException(status_code=404, detail=f"question not found: {qid}")

    if not bool(q["enabled"]):
        raise HTTPException(status_code=409, detail=f"question disabled: {qid}")

    return {
        "id": int(q["id"]),
        "axis_key": q["axis_key"],
        "question_text": q["question_text"],
        "choice_a": q["choice_a"],
        "choice_b": q["choice_b"],
        "enabled": bool(q["enabled"]),
    }