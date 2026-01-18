from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.answer import AnswerRequest, AnswerResponse

router = APIRouter()

SESSION_QUESTION_LIMIT = 5
MAX_QUESTIONS = 380

ALLOWED_VALUE_KEYS = {
    "self_direction",
    "conformity",
    "stimulation",
    "security",
    "hedonism",
    "tradition",
    "achievement",
    "benevolence",
    "power",
    "universalism",
}

# 이 부분은 이후 gpt 호출단으로 수정
def _reaction_text(session_question_index: int) -> str:
    if session_question_index >= SESSION_QUESTION_LIMIT:
        return "좋아. 오늘은 여기까지 해보자."
    return f"오케이. ({session_question_index}/{SESSION_QUESTION_LIMIT}) 다음으로 가보자."

@router.post("", response_model=AnswerResponse)
def post_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    qid = int(req.question_id)
    choice = req.choice

    # 0) 세션 존재/종료 체크
    ses = db.execute(
        text("SELECT id, ended_at FROM sessions WHERE id = :sid"),
        {"sid": sid}
    ).mappings().first()

    if not ses:
        raise HTTPException(status_code=404, detail=f"session not found: {sid}")
    if ses["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 중복 제출 방지: 같은 session_id + question_id 이미 있으면 409
    dup = db.execute(
        text("""
            SELECT id
            FROM answers
            WHERE session_id = :sid AND question_id = :qid
            LIMIT 1
        """),
        {"sid": sid, "qid": qid}
    ).mappings().first()

    if dup:
        raise HTTPException(status_code=409, detail="already answered")

    # 1) 질문 조회(가치키 포함)
    q = db.execute(
        text("""
            SELECT id, enabled, value_a_key, value_b_key
            FROM questions
            WHERE id = :qid
        """),
        {"qid": qid}
    ).mappings().first()

    if not q:
        raise HTTPException(status_code=404, detail=f"question not found: {qid}")
    if not bool(q["enabled"]):
        raise HTTPException(status_code=409, detail=f"question disabled: {qid}")

    value_a_key = q.get("value_a_key")
    value_b_key = q.get("value_b_key")

    # 2) chosen_value_key 결정
    if choice == "A":
        chosen_value_key = (value_a_key or "").strip()
    else:
        chosen_value_key = (value_b_key or "").strip()

    if not chosen_value_key:
        raise HTTPException(status_code=400, detail="chosen_value_key is empty (check value_a_key/value_b_key)")

    # 3) value key whitelist 검증
    if chosen_value_key not in ALLOWED_VALUE_KEYS:
        raise HTTPException(status_code=400, detail=f"invalid chosen_value_key: {chosen_value_key}")

    try:
        # current_question 일치 검증 (전역 번호 꼬임 방지)
        st = db.execute(
            text("""
                SELECT current_question
                FROM psano_state
                WHERE id = 1
            """)
        ).mappings().first()

        if not st:
            raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

        current_q = int(st["current_question"])
        if current_q != qid:
            raise HTTPException(status_code=409, detail="question_id mismatch with current_question")

        # 4) answers 저장
        db.execute(
            text("""
                INSERT INTO answers (session_id, question_id, choice, chosen_value_key)
                VALUES (:sid, :qid, :choice, :chosen_value_key)
            """),
            {"sid": sid, "qid": qid, "choice": choice, "chosen_value_key": chosen_value_key}
        )

        # 5) psano_personality +1
        col = chosen_value_key
        db.execute(
            text(f"UPDATE psano_personality SET `{col}` = `{col}` + 1 WHERE id = 1")
        )

        # 6) session_question_index 계산(방금 저장했으니 COUNT가 곧 index)
        cnt_row = db.execute(
            text("SELECT COUNT(*) AS cnt FROM answers WHERE session_id = :sid"),
            {"sid": sid}
        ).mappings().first()
        answered_cnt = int(cnt_row["cnt"]) if cnt_row else 0
        session_question_index = answered_cnt
        session_should_end = (session_question_index >= SESSION_QUESTION_LIMIT)

        # 다음 질문을 current+1이 아니라 "다음 enabled"로 세팅 (안정)
        next_q = db.execute(
            text("""
                SELECT id
                FROM questions
                WHERE id > :qid AND enabled = 1
                ORDER BY id ASC
                LIMIT 1
            """),
            {"qid": current_q}
        ).mappings().first()

        if next_q:
            new_current_q = int(next_q["id"])
        else:
            # 더 없으면 formation 완료로 처리되게 MAX+1로 보내기
            new_current_q = MAX_QUESTIONS + 1

        db.execute(
            text("""
                UPDATE psano_state
                SET current_question = :new_q
                WHERE id = 1
            """),
            {"new_q": new_current_q}
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    # next_question은 세션 종료면 None, 아니면 다음 current_question(단, formation 끝났으면 None)
    next_question = None
    if not session_should_end and new_current_q <= MAX_QUESTIONS:
        next_question = new_current_q

    return {
        "ok": True,
        "session_should_end": session_should_end,
        "session_question_index": session_question_index,
        "chosen_value_key": chosen_value_key,
        "assistant_reaction_text": _reaction_text(session_question_index),
        "next_question": next_question,
    }
