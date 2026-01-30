import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.common import Status
from schemas.monologue import (
    MonologueRequest, MonologueResponse,
    NudgeRequest, NudgeResponse
)

from services.llm_service import call_llm
from util.utils import trim, summary_to_text, load_growth_stage
from util.talk_utils import apply_policy_guard, OUTPUT_LIMIT

router = APIRouter()

FALLBACK_LINES = [
    "잠깐, 생각이 물에 잠겼어.",
    "말이 오기 전에 숨이 먼저 지나가.",
    "지금은 한 문장만 남겨둘게.",
]


def _apply_policy_guard(db: Session, text_for_check: str, user_text: str = ""):
    """apply_policy_guard 래퍼 (하위 호환성)"""
    return apply_policy_guard(db, text_for_check, user_text)


# -----------------------
# Idle monologue (1번)
# -----------------------

def _answered_total(db: Session) -> int:
    # 지금은 answers COUNT를 쓰는 버전 (안정적)
    try:
        n = db.execute(text("SELECT COUNT(*) FROM answers")).scalar()
        return int(n or 0)
    except Exception:
        return 0


def _char_budget(sentence_length_label: str) -> int:
    lab = (sentence_length_label or "").strip()
    if lab == "매우 짧음":
        return 60
    if lab == "짧음":
        return 80
    if lab == "보통":
        return 110
    return 140


def build_idle_monologue_prompt(*, persona: str | None, values_summary, stage, answered_total: int) -> str:
    persona = (persona or "").strip()
    summary_text = summary_to_text(values_summary).strip()

    # stage가 None일 경우 기본값 처리
    stage = stage or {}

    budget = _char_budget(stage.get("sentence_length"))
    metaphor = float(stage.get("metaphor_density") or 0.3)
    certainty = float(stage.get("certainty") or 0.4)
    empathy = float(stage.get("empathy_level") or 0.6)

    metaphor_guide = "은유는 거의 쓰지 마." if metaphor <= 0.25 else \
                     "은유는 가끔만 써." if metaphor <= 0.45 else \
                     "은유를 자주 섞어."
    certainty_guide = "단정하지 말고 조심스럽게 말해." if certainty <= 0.45 else \
                      "너무 단정하진 말되, 어느 정도 확신을 담아."
    empathy_guide = "공감 표현을 조금 더 해줘." if empathy >= 0.7 else \
                    "공감은 과하지 않게 해."

    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")

    base.append(
        f"""너는 전시 작품 '사노'다.
지금은 관람객의 직접 입력이 없는 상태에서, 짧게 혼잣말을 한다.

[성장단계]
- stage: {stage.get("stage_name_kr")} ({stage.get("stage_name_en")})
- answered_total: {answered_total}
- 말투 예시: {stage.get("notes") or ""}

규칙:
- 한국어
- {budget}자 내외(최대 {OUTPUT_LIMIT}자 절대 초과 금지)
- 문장 1~2개
- 과장된 감정 표현 금지
- 위험하거나 민감한 주제(자해/폭력/혐오/정치 선동 등) 언급 금지
- 관람객에게 "대놓고 질문"하지 말 것(물음표는 많아도 1개)
- 위 [말투 예시]의 톤과 어미를 참고해서 말해

스타일 지시:
- {metaphor_guide}
- {certainty_guide}
- {empathy_guide}

혼잣말 1개를 생성해줘."""
    )
    return "\n".join(base).strip()


@router.post("", response_model=MonologueResponse)
def idle_monologue(req: MonologueRequest, db: Session = Depends(get_db)):
    if req.answered_total_override is not None:
        answered_total = int(req.answered_total_override)
    else:
        answered_total = _answered_total(db)

    stage = load_growth_stage(db, answered_total) or {}

    st = db.execute(
        text("""
            SELECT persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    persona = (st or {}).get("persona_prompt")
    values_summary = (st or {}).get("values_summary")

    prompt = build_idle_monologue_prompt(
        persona=persona,
        values_summary=values_summary,
        stage=stage,
        answered_total=answered_total,
    )

    # (선택) 정책 필터
    policy = _apply_policy_guard(db, prompt)
    if policy:
        return {
            "status": policy["status"],
            "monologue_text": policy["assistant_text"],
            "fallback_code": policy["fallback_code"],
            "answered_total": int(answered_total),
            "stage_id": int(stage.get("stage_id") or 1),
            "stage_name_kr": stage.get("stage_name_kr") or "태동기",
            "stage_name_en": stage.get("stage_name_en") or "Nascent",
        }

    # LLM 호출 (설정: psano_config에서 로드)
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
        db=db,
        model=req.model,
        max_tokens=req.max_output_tokens or 800,  # GPT-5 reasoning 모델 대응
        fallback_text=fallback_text,
    )

    if result.success:
        status = Status.ok
        monologue_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = None
    else:
        status = Status.fallback
        monologue_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = result.fallback_code

    return {
        "status": status,
        "monologue_text": monologue_text,
        "fallback_code": fallback_code,
        "answered_total": int(answered_total),
        "stage_id": int(stage.get("stage_id") or 1),
        "stage_name_kr": stage.get("stage_name_kr") or "태동기",
        "stage_name_en": stage.get("stage_name_en") or "Nascent",
    }


# -----------------------
# Nudge (대화 중 혼잣말)
# -----------------------

def _load_idle(db: Session, idle_id: int):
    """idle 혼잣말 로드"""
    return db.execute(
        text("""
            SELECT id, axis_key, question_text, value
            FROM psano_idle
            WHERE id = :id
        """),
        {"id": idle_id}
    ).mappings().first()


def _get_recent_messages(db: Session, sid: int, limit: int = 6):
    """idle_talk_messages에서 최근 메시지 조회 (시간순 정렬)"""
    limit = max(2, min(int(limit or 6), 12))
    rows = db.execute(
        text("""
            SELECT user_text, assistant_text
            FROM idle_talk_messages
            WHERE session_id = :sid
            ORDER BY id DESC
            LIMIT :lim
        """),
        {"sid": int(sid), "lim": int(limit)}
    ).mappings().all()
    # 최신 -> 과거 순으로 왔으니 뒤집어서 시간순으로
    return list(rows)[::-1]


def build_nudge_prompt(*, persona: str | None, values_summary, idle_ctx: str, recent_msgs: list, session_memory: str | None):
    """nudge 프롬프트 생성"""
    persona = (persona or "").strip()
    summary_text = summary_to_text(values_summary).strip()
    mem = (session_memory or "").strip()

    convo_lines = []
    for r in recent_msgs:
        u = (r.get("user_text") or "").strip()
        a = (r.get("assistant_text") or "").strip()

        # nudge 로그는 user_text가 "[nudge]"일 수 있으니 표시
        if u and u != "[nudge]":
            convo_lines.append(f"User: {u}")
        elif u == "[nudge]":
            convo_lines.append(f"(nudge)")
        if a:
            convo_lines.append(f"Assistant: {a}")

    convo = "\n".join(convo_lines).strip()

    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")

    base.append(idle_ctx)

    if mem:
        base.append(f"[session_memory]\n{mem}\n")

    if convo:
        base.append(f"[recent_conversation]\n{convo}\n")

    base.append(
        f"""너는 전시 작품 '사노'다.
지금은 대화 도중, 사용자의 반응이 잠깐 멈춘 상황이다.
위 혼잣말과 방금까지의 대화 흐름을 살려서, 짧은 혼잣말/툭 던지는 한마디를 만든다.

규칙:
- 한국어
- 최대 {OUTPUT_LIMIT}자
- 문장 1~2개
- 과장된 감정 표현 금지
- persona_prompt의 SAFETY 규칙에 따라 민감 주제 처리
- 사용자를 재촉하지 말 것("빨리", "왜 답 안 해" 금지)
- 질문은 있어도 1개까지만

출력은 문장만, 다른 라벨/설명 없이."""
    )
    return "\n".join(base).strip()


@router.post("/nudge", response_model=NudgeResponse)
def talk_nudge(req: NudgeRequest, db: Session = Depends(get_db)):
    """
    POST /monologue/nudge
    대화 중 사용자 반응이 없을 때 사노가 툭 던지는 한마디
    """
    sid = int(req.session_id)

    # 1) psano_state (persona/summary)
    st = db.execute(
        text("""
            SELECT persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    persona = (st or {}).get("persona_prompt")
    values_summary = (st or {}).get("values_summary")

    # 2) 세션 체크 (talk 시작 했는지)
    sess = db.execute(
        text("""
            SELECT id, ended_at, idle_id, idle_talk_memory
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": sid}
    ).mappings().first()

    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    idle_id = sess.get("idle_id")
    if idle_id in (None, "", 0):
        raise HTTPException(status_code=409, detail="talk not started for this session. call POST /talk/start first.")

    idle_id = int(idle_id)
    session_memory = sess.get("idle_talk_memory")

    # 3) idle 컨텍스트 로드
    idle = _load_idle(db, idle_id)
    if not idle:
        raise HTTPException(status_code=404, detail=f"idle not found: {idle_id}")

    monologue = (idle.get("question_text") or "").strip()
    axis_key = (idle.get("axis_key") or "").strip()
    idle_ctx = f"[idle_monologue]\n- axis: {axis_key}\n- text: {monologue}\n"

    # 4) 최근 대화 조회
    recent_msgs = _get_recent_messages(db, sid, req.recent_messages or 6)

    # 5) 프롬프트 생성
    prompt = build_nudge_prompt(
        persona=persona,
        values_summary=values_summary,
        idle_ctx=idle_ctx,
        recent_msgs=recent_msgs,
        session_memory=session_memory,
    )

    # 6) 정책 필터
    user_texts = "\n".join([m.get("user_text", "") for m in recent_msgs if m])
    policy = _apply_policy_guard(db, idle_ctx + "\n" + user_texts, user_texts)
    if policy:
        nudge_text = policy["assistant_text"]
        fallback_code = policy["fallback_code"]
        status = Status.fallback
    else:
        # LLM 호출
        fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
        result = call_llm(
            prompt,
            db=db,
            model=req.model,
            max_tokens=req.max_output_tokens or 800,
            fallback_text=fallback_text,
        )

        if result.success:
            status = Status.ok
            nudge_text = trim(result.content, OUTPUT_LIMIT)
            fallback_code = None
        else:
            status = Status.fallback
            nudge_text = trim(result.content, OUTPUT_LIMIT)
            fallback_code = result.fallback_code

    # 7) idle_talk_messages 저장 (nudge 마킹)
    db.execute(
        text("""
            INSERT INTO idle_talk_messages (session_id, idle_id, user_text, assistant_text, status)
            VALUES (:sid, :iid, :u, :a, :s)
        """),
        {
            "sid": sid,
            "iid": idle_id,
            "u": "[nudge]",
            "a": nudge_text,
            "s": status.value,
        }
    )
    db.commit()

    return {
        "status": status,
        "nudge_text": nudge_text,
        "fallback_code": fallback_code,
        "session_id": sid,
        "idle_id": idle_id,
    }
