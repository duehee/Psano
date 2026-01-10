from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.answer import AnswerRequest, AnswerResponse

router = APIRouter()

MAX_QUESTIONS = 380

@router.post("", response_model=AnswerResponse)
def submit_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    choice_val = getattr(req.choice, "value", req.choice)

    try:
        with db.begin():
            # 1) 현재 상태 읽기
            st = db.execute(
                text("""
                    SELECT phase, current_question
                    FROM psano_state
                    WHERE id = 1
                    FOR UPDATE
                """)
            ).mappings().first()

            if not st:
                raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

            if st["phase"] != "formation":
                raise HTTPException(status_code=409, detail="phase is not formation")

            current_q = int(st["current_question"])

            # 2) 세션 존재/유효 확인 (ended_at NULL 인지까지)
            sess = db.execute(
                text("""
                    SELECT id, ended_at
                    FROM sessions
                    WHERE id = :sid
                """),
                {"sid": req.session_id}
            ).mappings().first()

            if not sess:
                raise HTTPException(status_code=404, detail="session not found")

            if sess["ended_at"] is not None:
                raise HTTPException(status_code=409, detail="session already ended")

            # 3) 순차 해금 규칙: 현재 열린 질문만 허용
            if int(req.question_id) != current_q:
                raise HTTPException(status_code=409, detail=f"only current question allowed: {current_q}")

            # 4) 질문 존재/활성 확인
            q = db.execute(
                text("""
                    SELECT id, enabled
                    FROM questions
                    WHERE id = :qid
                """),
                {"qid": current_q}
            ).mappings().first()

            if not q:
                raise HTTPException(status_code=404, detail=f"question not found: {current_q}")

            if not bool(q["enabled"]):
                raise HTTPException(status_code=409, detail=f"question disabled: {current_q}")

            # 5) 중복 방지: 세션당 같은 질문 1회
            dup = db.execute(
                text("""
                    SELECT id
                    FROM answers
                    WHERE session_id = :sid AND question_id = :qid
                    LIMIT 1
                """),
                {"sid": req.session_id, "qid": current_q}
            ).mappings().first()

            if dup:
                raise HTTPException(status_code=409, detail="already answered")

            # 6) 저장
            db.execute(
                text("""
                    INSERT INTO answers (session_id, question_id, choice, created_at)
                    VALUES (:sid, :qid, :choice, NOW())
                """),
                {"sid": req.session_id, "qid": current_q, "choice": choice_val}
            )

            # 7) 다음 질문 해금(전역)
            next_q = current_q + 1

            if next_q > MAX_QUESTIONS:
                # formation 완료 → chat 전환
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase='chat',
                            current_question=:next_q,
                            formed_at=NOW()
                        WHERE id=1
                    """),
                    {"next_q": next_q}
                )
                return {"saved": True, "next_question": None}

            db.execute(
                text("""
                    UPDATE psano_state
                    SET current_question=:next_q
                    WHERE id=1
                """),
                {"next_q": next_q}
            )

            return {"saved": True, "next_question": next_q}

    except HTTPException:
        raise
    except Exception as e:
        # 그 외는 500
        raise HTTPException(status_code=500, detail=str(e))