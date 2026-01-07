import time
import uuid

from fastapi import APIRouter, HTTPException
from schemas import SessionStartResponse, SessionEndRequest, BasicStatusResponse
from storage import SESSIONS, GLOBAL_STATE, with_lock

router = APIRouter(tags=["session"])

def _require_session(session_id: str):
    s = SESSIONS.get(session_id)
    if not s or s.get("ended_at") is not None:
        raise HTTPException(status_code=400, detail="Invalid or ended session_id")
    return s

@router.post("/start", response_model=SessionStartResponse)
@with_lock
def session_start():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "session_id": session_id,
        "started_at": time.time(),
        "ended_at": None,
    }
    return {
        "session_id": session_id,
        "stage": GLOBAL_STATE["stage"],
        "values": GLOBAL_STATE["values"],
    }

@router.post("/end", response_model=BasicStatusResponse)
@with_lock
def session_end(req: SessionEndRequest):
    s = _require_session(req.session_id)
    s["ended_at"] = time.time()
    s["end_reason"] = req.reason
    return {"ok": True}