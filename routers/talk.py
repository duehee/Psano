import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.talk import TalkRequest, TalkResponse
from schemas.common import Status
from database import get_db

from openai import OpenAI

client = OpenAI()

router = APIRouter()

FALLBACK_LINES = [
    "지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.",
    "나는 아직 정리 중이야. 너의 질문이 물결처럼 남아 있어.",
    "답을 급히 만들고 싶진 않아. 한 번만 더 천천히 말해줄래?",
]

def build_prompt(user_text: str, persona: str | None, summary: dict | None) -> str:
    persona = persona or "You are Psano."
    summary = summary or {}
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary}\n"
        f"User: {user_text}\n"
        "Assistant:"
    )

@router.post("", response_model=TalkResponse)
def talk(req: TalkRequest, db: Session = Depends(get_db)):
    # 1) psano_state 읽기 (phase / persona_prompt / values_summary)
    st = db.execute(
        text("""
            SELECT phase, persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # ✅ 테스트용: formation에서도 talk 허용하고 싶으면 True로 바꿔
    ALLOW_TALK_IN_FORMATION = True

    if st["phase"] != "chat" and not ALLOW_TALK_IN_FORMATION:
        raise HTTPException(status_code=409, detail="phase is not chat")

    # 2) 세션 존재/진행중 체크 (ended_at이 NULL인 세션만 허용)
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

    # ended_at 컬럼이 있다면 진행중만 허용
    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 3) 프롬프트 구성
    prompt = build_prompt(
        user_text=req.user_text,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
    )

    # 4) GPT 호출 (실패하면 fallback)
    status = Status.ok
    assistant_text = ""

    try:
        resp = client.responses.create(
            model=getattr(req, "model", "gpt-4.1-mini"),
            input=prompt,
            max_output_tokens=getattr(req, "max_output_tokens", 180),
        )
        assistant_text = (resp.output_text or "").strip()
        if not assistant_text:
            raise RuntimeError("empty output")
        status = Status.ok
    except Exception:
        status = Status.fallback
        assistant_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]

    # 5) ✅ DB 저장: talk_messages
    # (테이블 컬럼: session_id, user_text, assistant_text, status, created_at)
    try:
        db.execute(
            text("""
                INSERT INTO talk_messages (session_id, user_text, assistant_text, status)
                VALUES (:sid, :u, :a, :s)
            """),
            {
                "sid": req.session_id,
                "u": req.user_text,
                "a": assistant_text,
                "s": status.value if hasattr(status, "value") else str(status),
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        pass

    return {"status": status, "ui_text": assistant_text}