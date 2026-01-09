from fastapi import APIRouter, HTTPException
from schemas.answer import AnswerRequest, AnswerResponse
from routers._store import (
    LOCK, GLOBAL_STATE, SESSIONS, ANSWERS,
    ensure_question_exists, now_ts, MAX_QUESTIONS
)

router = APIRouter()

@router.post("", response_model=AnswerResponse)
def submit_answer(req: AnswerRequest):
    with LOCK:
        if GLOBAL_STATE["phase"] != "formation":
            raise HTTPException(status_code=409, detail="phase is not formation")

        sess = SESSIONS.get(req.session_id)
        if not sess:
            raise HTTPException(status_code=404, detail="session not found")

        # 현재 열린 질문만 받는다(순차 해금 규칙)
        current_q = int(GLOBAL_STATE["current_question"])
        if req.question_id != current_q:
            raise HTTPException(status_code=409, detail=f"only current question allowed: {current_q}")

        # 질문 존재 확인
        try:
            ensure_question_exists(req.question_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))

        # 중복 방지(세션당 같은 질문 1회)
        for a in ANSWERS:
            if a["session_id"] == req.session_id and a["question_id"] == req.question_id:
                raise HTTPException(status_code=409, detail="already answered")

        ANSWERS.append({
            "session_id": req.session_id,
            "question_id": req.question_id,
            "choice": req.choice.value,
            "created_at": now_ts(),
        })

        # 다음 질문 해금(전역 진행)
        GLOBAL_STATE["current_question"] = current_q + 1

        # 380개 완료 -> chat 전환
        if GLOBAL_STATE["current_question"] > MAX_QUESTIONS:
            GLOBAL_STATE["phase"] = "chat"
            GLOBAL_STATE["formed_at"] = now_ts()
            # persona_prompt / values_summary는 나중에 집계해서 채우면 됨
            if GLOBAL_STATE["persona_prompt"] is None:
                GLOBAL_STATE["persona_prompt"] = "Psano persona (placeholder)."
            if GLOBAL_STATE["values_summary"] is None:
                GLOBAL_STATE["values_summary"] = {"note": "placeholder summary"}

            return {"saved": True, "next_question": None}

        return {"saved": True, "next_question": int(GLOBAL_STATE["current_question"])}