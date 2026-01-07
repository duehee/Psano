import time
from fastapi import APIRouter, HTTPException, Query

from schemas import TeachQuestionResponse, TeachAnswerRequest, UiResponse
from storage import GLOBAL_STATE, SESSIONS, with_lock
from docs.questions import TEACH_QUESTIONS

router = APIRouter(tags=["teach"])

def _require_session(session_id: str):
    s = SESSIONS.get(session_id)
    if not s or s.get("ended_at") is not None:
        raise HTTPException(status_code=400, detail="Invalid or ended session_id")
    return s

def _recompute_stage(total_teach_count: int) -> int:
    # 임시 규칙: 60개 단위로 stage 증가, 6 이후 순환
    return int((total_teach_count // 60) % 6 + 1)

@router.get("/question", response_model=TeachQuestionResponse)
def teach_question(session_id: str = Query(..., min_length=1)):
    _require_session(session_id)
    idx = GLOBAL_STATE["total_teach_count"] % len(TEACH_QUESTIONS)
    return TEACH_QUESTIONS[idx]

@router.post("/answer", response_model=UiResponse)
@with_lock
def teach_answer(req: TeachAnswerRequest):
    _require_session(req.session_id)

    q = next((x for x in TEACH_QUESTIONS if x["question_id"] == req.question_id), None)
    if q is None:
        raise HTTPException(status_code=400, detail="Invalid question_id")

    GLOBAL_STATE["total_teach_count"] += 1
    GLOBAL_STATE["stage"] = _recompute_stage(GLOBAL_STATE["total_teach_count"])
    GLOBAL_STATE["updated_at"] = time.time()

    return UiResponse(
        status="ok",
        ui_text="(사노가 조용히 고개를 끄덕인다.)",
        stage=GLOBAL_STATE["stage"],
        values=GLOBAL_STATE["values"],
        next_action="teach_done",
    )