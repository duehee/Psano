from fastapi import APIRouter
from schemas.state import StateResponse
from routers._store import LOCK, GLOBAL_STATE

router = APIRouter()

@router.get("", response_model=StateResponse)
def get_state():
    with LOCK:
        formed_at = GLOBAL_STATE["formed_at"]
        formed_iso = None
        if formed_at is not None:
            # 간단히 epoch를 문자열로(원하면 datetime ISO로 바꿔도 됨)
            formed_iso = str(formed_at)

        return {
            "phase": GLOBAL_STATE["phase"],
            "current_question": int(GLOBAL_STATE["current_question"]),
            "formed_at": formed_iso,
        }