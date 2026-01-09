from fastapi import APIRouter, HTTPException
from schemas.talk import TalkRequest, TalkResponse
from schemas.common import Status
from routers._store import LOCK, GLOBAL_STATE, SESSIONS, now_ts, ANSWERS, QUESTIONS, MAX_QUESTIONS
from openai import OpenAI

client = OpenAI()

router = APIRouter()

FALLBACK_LINES = [
    "지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.",
    "나는 아직 정리 중이야. 너의 질문이 물결처럼 남아 있어.",
    "답을 급히 만들고 싶진 않아. 한 번만 더 천천히 말해줄래?",
]

def build_prompt(user_text: str) -> str:
    # 나중에 persona_prompt + values_summary를 붙이면 됨
    persona = GLOBAL_STATE.get("persona_prompt") or "You are Psano."
    summary = GLOBAL_STATE.get("values_summary") or {}
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary}\n"
        f"User: {user_text}\n"
        "Assistant:"
    )

@router.post("", response_model=TalkResponse)
def talk(req: TalkRequest):
    # ✅ 테스트용: phase/session 검사 잠깐 스킵
    # with LOCK:
    #     phase = GLOBAL_STATE["phase"]
    #     allow = bool(GLOBAL_STATE.get("allow_talk_in_formation", False))
    #     if phase != "chat" and not allow:
    #         raise HTTPException(status_code=409, detail="phase is not chat")
    #     if req.session_id not in SESSIONS:
    #         raise HTTPException(status_code=404, detail="session not found")

    prompt = build_prompt(req.user_text)

    if client is not None:
        try:
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                max_output_tokens=180,
            )
            text = (resp.output_text or "").strip()
            if not text:
                raise RuntimeError("empty output")
            return {"status": Status.ok, "ui_text": text}
        except Exception as e:
            pass

    idx = min(len(req.user_text) % len(FALLBACK_LINES), len(FALLBACK_LINES) - 1)
    return {"status": Status.fallback, "ui_text": FALLBACK_LINES[idx]}