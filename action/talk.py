import time
from fastapi import APIRouter

from schemas import TalkRequest, UiResponse
from storage import GLOBAL_STATE, SESSIONS, with_lock
from docs.fallbacks import FALLBACK_LINES
from prompts import minimal_prompt
from deps import client

router = APIRouter(tags=["talk"])

def _require_session(session_id: str):
    s = SESSIONS.get(session_id)
    if not s or s.get("ended_at") is not None:
        # talk는 UI쪽에서 자주 치니까 에러보단 fallback으로 돌려도 됨
        # 근데 여기서는 명확히 막을게(원하면 바꿔도 됨)
        raise ValueError("Invalid or ended session_id")
    return s

@router.post("", response_model=UiResponse)
@with_lock
def talk(req: TalkRequest):
    try:
        _require_session(req.session_id)
    except Exception:
        ui_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
        return UiResponse(
            status="fallback",
            ui_text=ui_text,
            stage=GLOBAL_STATE["stage"],
            values=GLOBAL_STATE["values"],
            next_action="talk_done",
        )

    prompt = minimal_prompt(req.user_text, GLOBAL_STATE["stage"], GLOBAL_STATE["values"])

    try:
        resp = client.responses.create(
            model=req.model,
            input=prompt,
            max_output_tokens=req.max_output_tokens,
        )
        ui_text = (resp.output_text or "").strip()

        status = "ok" if ui_text else "fallback"
        if not ui_text:
            ui_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]

        GLOBAL_STATE["total_talk_count"] += 1
        GLOBAL_STATE["updated_at"] = time.time()

        return UiResponse(
            status=status,
            ui_text=ui_text,
            stage=GLOBAL_STATE["stage"],
            values=GLOBAL_STATE["values"],
            next_action="talk_done",
        )
    except Exception:
        ui_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
        return UiResponse(
            status="fallback",
            ui_text=ui_text,
            stage=GLOBAL_STATE["stage"],
            values=GLOBAL_STATE["values"],
            next_action="talk_done",
        )