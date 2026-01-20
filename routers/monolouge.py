import time
import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI

from database import get_db
from schemas.common import Status
from schemas.monologue import (
    MonologueRequest, MonologueResponse,
    NudgeRequest, NudgeResponse
)

# (선택) 정책 필터 재사용하고 싶으면 import
from routers.talk_policy import moderate_text, Action


OUTPUT_LIMIT = 150
client = OpenAI()

router = APIRouter()

FALLBACK_LINES = [
    "잠깐, 생각이 물에 잠겼어.",
    "말이 오기 전에 숨이 먼저 지나가.",
    "지금은 한 문장만 남겨둘게.",
]


def _trim(s: str, n: int) -> str:
    s = (s or "").strip()
    return s[:n] if len(s) > n else s


def _summary_to_text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except Exception:
            return str(v)
    return str(v)


def _policy_message(action: Action) -> str:
    # nudge/idle은 아주 짧게
    if action == Action.REDIRECT:
        return "조금 다른 쪽에서 생각해볼까."
    if action == Action.WARN_END:
        return "오늘은 여기까지가 좋겠어."
    if action == Action.BLOCK:
        return "그 방향은 여기선 다루기 어려워."
    if action == Action.PRIVACY:
        return "개인정보는 말하지 말아줘."
    if action == Action.CRISIS:
        return "지금 위험하면 112/119에 연락해. 자살예방 109도 있어."
    return FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]


def _apply_policy_guard(text_for_check: str):
    """
    CRISIS(자해/자살)와 PRIVACY(개인정보 regex)만 즉시 차단.
    나머지(성적/혐오/범죄/정치/종교)는 LLM이 프롬프트 가이드에 따라 자연스럽게 처리.
    """
    hit = moderate_text(text_for_check)
    if not hit:
        return None

    rule, _kw = hit

    # CRISIS나 PRIVACY만 즉시 차단 (나머지는 LLM이 처리)
    if rule.action not in (Action.CRISIS, Action.PRIVACY):
        return None

    msg = _policy_message(rule.action)
    return {
        "status": Status.fallback,
        "assistant_text": _trim(msg, OUTPUT_LIMIT),
        "fallback_code": getattr(rule.fallback_id, "value", str(rule.fallback_id)),
        "policy_category": rule.category,
    }


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


def _load_growth_stage(db: Session, answered_total: int):
    row = db.execute(
        text("""
            SELECT stage_id, stage_name_kr, stage_name_en,
                   min_answers, max_answers, metaphor_density, certainty,
                   sentence_length, empathy_level, notes
            FROM psano_growth_stages
            WHERE :n BETWEEN min_answers AND max_answers
            ORDER BY stage_id ASC
            LIMIT 1
        """),
        {"n": int(answered_total)},
    ).mappings().first()

    if row:
        return row

    row2 = db.execute(
        text("""
            SELECT stage_id, stage_name_kr, stage_name_en,
                   min_answers, max_answers, metaphor_density, certainty,
                   sentence_length, empathy_level, notes
            FROM psano_growth_stages
            ORDER BY stage_id DESC
            LIMIT 1
        """)
    ).mappings().first()

    return row2


def _char_budget(sentence_length_label: str) -> int:
    lab = (sentence_length_label or "").strip()
    if lab == "매우 짧음":
        return 60
    if lab == "짧음":
        return 80
    if lab == "보통":
        return 110
    return 140


def build_idle_monologue_prompt(*, persona: str | None, values_summary, stage: dict, answered_total: int) -> str:
    persona = (persona or "").strip()
    summary_text = _summary_to_text(values_summary).strip()

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
- style hints: {stage.get("notes") or ""}

규칙:
- 한국어
- {budget}자 내외(최대 {OUTPUT_LIMIT}자 절대 초과 금지)
- 문장 1~2개
- 과장된 감정 표현 금지
- 위험하거나 민감한 주제(자해/폭력/혐오/정치 선동 등) 언급 금지
- 관람객에게 "대놓고 질문"하지 말 것(물음표는 많아도 1개)

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

    stage = _load_growth_stage(db, answered_total)

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
    policy = _apply_policy_guard(prompt)
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

    status = Status.ok
    fallback_code = None
    monologue_text = ""

    try:
        resp = client.chat.completions.create(
            model=req.model or "gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=req.max_output_tokens or 120,
        )
        monologue_text = _trim(resp.choices[0].message.content or "", OUTPUT_LIMIT)
        if not monologue_text:
            raise RuntimeError("empty output")
        status = Status.ok
    except Exception:
        status = Status.fallback
        fallback_code = "LLM_FAILED"
        monologue_text = _trim(FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)], OUTPUT_LIMIT)

    return {
        "status": status,
        "monologue_text": monologue_text,
        "fallback_code": fallback_code,
        "answered_total": int(answered_total),
        "stage_id": int(stage.get("stage_id") or 1),
        "stage_name_kr": stage.get("stage_name_kr") or "태동기",
        "stage_name_en": stage.get("stage_name_en") or "Nascent",
    }

def _load_topic(db: Session, topic_id: int):
    row = db.execute(
        text("""
            SELECT id, title, description
            FROM talk_topics
            WHERE id = :tid
        """),
        {"tid": int(topic_id)}
    ).mappings().first()
    return row


def _topic_context(db: Session, topic_id: int) -> str:
    topic = _load_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="topic not found")
    title = (topic.get("title") or "").strip()
    desc = (topic.get("description") or "").strip()
    return f"[topic]\n- title: {title}\n- description: {desc}\n"


def _read_session_talk_fields(db: Session, sid: int):
    # 컬럼 버전 차이 안전 처리
    try:
        return db.execute(
            text("""
                SELECT id, ended_at, topic_id, talk_memory, turn_count
                FROM sessions
                WHERE id = :sid
            """),
            {"sid": int(sid)}
        ).mappings().first()
    except Exception:
        return db.execute(
            text("""
                SELECT id, ended_at
                FROM sessions
                WHERE id = :sid
            """),
            {"sid": int(sid)}
        ).mappings().first()


def _get_recent_messages(db: Session, sid: int, limit: int = 6):
    limit = max(2, min(int(limit or 6), 12))

    # created_at이 있으면 그걸 쓰고, 없으면 id로 정렬
    try:
        rows = db.execute(
            text("""
                SELECT user_text, assistant_text
                FROM talk_messages
                WHERE session_id = :sid
                ORDER BY id DESC
                LIMIT :lim
            """),
            {"sid": int(sid), "lim": int(limit)}
        ).mappings().all()
    except Exception:
        rows = []

    # 최신 -> 과거 순으로 왔으니 뒤집어서 시간순으로
    rows = list(rows)[::-1]
    return rows


def build_nudge_prompt(*, persona: str | None, values_summary, topic_ctx: str, recent_msgs: list, talk_memory: str | None):
    persona = (persona or "").strip()
    summary_text = _summary_to_text(values_summary).strip()
    mem = (talk_memory or "").strip()

    convo_lines = []
    for r in recent_msgs:
        u = (r.get("user_text") or "").strip()
        a = (r.get("assistant_text") or "").strip()

        # nudge 로그는 user_text가 "[nudge]"일 수 있으니 너무 길면 제외
        if u:
            convo_lines.append(f"User: {u}")
        if a:
            convo_lines.append(f"Assistant: {a}")

    convo = "\n".join(convo_lines).strip()

    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")

    base.append(topic_ctx)

    if mem:
        base.append(f"[session_memory]\n{mem}\n")

    if convo:
        base.append(f"[recent_conversation]\n{convo}\n")

    base.append(
        f"""너는 전시 작품 '사노'다.
지금은 대화 도중, 사용자의 반응이 잠깐 멈춘 상황이다.
주제와 방금까지의 대화 흐름을 살려서, 짧은 혼잣말/툭 던지는 한마디를 만든다.

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
    sess = _read_session_talk_fields(db, sid)
    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    topic_id = sess.get("topic_id")
    if topic_id in (None, "", 0):
        raise HTTPException(status_code=409, detail="talk not started for this session. call POST /talk/start first.")

    topic_id = int(topic_id)
    talk_memory = sess.get("talk_memory") if isinstance(sess, dict) else None

    # 3) topic + 최근 대화
    topic_ctx = _topic_context(db, topic_id)
    recent_msgs = _get_recent_messages(db, sid, req.recent_messages or 6)

    prompt = build_nudge_prompt(
        persona=persona,
        values_summary=values_summary,
        topic_ctx=topic_ctx,
        recent_msgs=recent_msgs,
        talk_memory=talk_memory,
    )

    # (선택) 정책 필터: topic/대화 기반으로 한번만
    policy = _apply_policy_guard(topic_ctx + "\n" + "\n".join([m.get("user_text","") for m in recent_msgs if m]) )
    if policy:
        nudge_text = policy["assistant_text"]
        fallback_code = policy["fallback_code"]
        status = Status.fallback
    else:
        status = Status.ok
        fallback_code = None
        nudge_text = ""

        try:
            resp = client.chat.completions.create(
                model=req.model or "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=req.max_output_tokens or 90,
            )
            nudge_text = _trim(resp.choices[0].message.content or "", OUTPUT_LIMIT)
            if not nudge_text:
                raise RuntimeError("empty output")
            status = Status.ok
        except Exception:
            status = Status.fallback
            fallback_code = "LLM_FAILED"
            nudge_text = _trim(FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)], OUTPUT_LIMIT)

    # 4) talk_messages 저장 (nudge 마킹)
    try:
        try:
            db.execute(
                text("""
                    INSERT INTO talk_messages (session_id, topic_id, user_text, assistant_text, status)
                    VALUES (:sid, :tid, :u, :a, :s)
                """),
                {
                    "sid": sid,
                    "tid": int(topic_id),
                    "u": "[nudge]",
                    "a": nudge_text,
                    "s": status.value if hasattr(status, "value") else str(status),
                }
            )
        except Exception:
            db.execute(
                text("""
                    INSERT INTO talk_messages (session_id, user_text, assistant_text, status)
                    VALUES (:sid, :u, :a, :s)
                """),
                {
                    "sid": sid,
                    "u": "[nudge]",
                    "a": nudge_text,
                    "s": status.value if hasattr(status, "value") else str(status),
                }
            )
        db.commit()
    except Exception:
        db.rollback()
        pass

    return {
        "status": status,
        "monologue_text": nudge_text,
        "fallback_code": fallback_code,
        "session_id": sid,
        "topic_id": int(topic_id),
    }
