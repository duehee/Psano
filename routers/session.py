from fastapi import APIRouter, HTTPException
from schemas.session import (
    SessionStartRequest, SessionStartResponse,
    SessionEndRequest, SessionEndResponse
)
from routers._store import LOCK, GLOBAL_STATE, SESSIONS, next_session_id, now_ts

router = APIRouter()

@router.post("/start", response_model=SessionStartResponse)
def start_session(req: SessionStartRequest):
    name = req.visitor_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="visitor_name is empty")

    with LOCK:
        sid = next_session_id()
        SESSIONS[sid] = {
            "id": sid,
            "visitor_name": name,
            "started_at": now_ts(),
            "ended_at": None,
            "end_reason": None,
        }
        return {
            "session_id": sid,
            "phase": GLOBAL_STATE["phase"],
            "current_question": int(GLOBAL_STATE["current_question"]),
        }


@router.post("/end", response_model=SessionEndResponse)
def end_session(req: SessionEndRequest):
    with LOCK:
        sess = SESSIONS.get(req.session_id)
        if not sess:
            raise HTTPException(status_code=404, detail="session not found")

        if sess["ended_at"] is None:
            sess["ended_at"] = now_ts()
            sess["end_reason"] = req.reason

        return {"session_id": req.session_id, "ended": True}