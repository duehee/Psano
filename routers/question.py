from fastapi import APIRouter, HTTPException
from schemas.question import QuestionResponse
from routers._store import LOCK, GLOBAL_STATE, ensure_question_exists, is_formation_done

router = APIRouter()

@router.get("/current", response_model=QuestionResponse)
def get_current_question():
    with LOCK:
        if GLOBAL_STATE["phase"] != "formation":
            raise HTTPException(status_code=409, detail="phase is not formation")

        if is_formation_done():
            raise HTTPException(status_code=409, detail="formation already completed")

        qid = int(GLOBAL_STATE["current_question"])
        try:
            q = ensure_question_exists(qid)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))

        return q