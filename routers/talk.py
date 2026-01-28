import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.session_service import end_session_core
from util.utils import iso, trim, summary_to_text, get_prompt

from schemas.talk import (
    TalkRequest,
    TalkResponse,
    TopicsResponse,
    TalkStartRequest,
    TalkStartResponse,
    TalkEndRequest,
    TalkEndResponse,
    IdleTalkStartRequest,
    IdleTalkStartResponse,
    IdleTalkTurnRequest,
    IdleTalkTurnResponse,
)

from schemas.common import Status
from routers.talk_policy import moderate_text, generate_policy_response, Action
from database import get_db
from services.llm_service import call_llm

INPUT_LIMIT = 200
OUTPUT_LIMIT = 150

# 세션 메모(요약 기억) 최대 길이
MEMORY_LIMIT = 600

# 최근 턴 몇 개를 넣을지 (talk_messages 한 행 = 1턴)
RECENT_TURNS = 3

router = APIRouter()

FALLBACK_LINES = [
    "지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.",
    "나는 아직 정리 중이야. 너의 질문이 물결처럼 남아 있어.",
    "답을 급히 만들고 싶진 않아. 한 번만 더 천천히 말해줄래?",
]


def _load_topic(db: Session, topic_id: int):
    row = db.execute(
        text(
            """
            SELECT id, title, description
            FROM talk_topics
            WHERE id = :tid
            """
        ),
        {"tid": int(topic_id)},
    ).mappings().first()
    return row


def _topic_context(db: Session, topic_id: int) -> str:
    topic = _load_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="topic not found")
    title = (topic.get("title") or "").strip()
    desc = (topic.get("description") or "").strip()
    return f"[topic]\n- title: {title}\n- description: {desc}\n"


def _apply_policy_guard(db: Session, text_for_check: str, user_text: str):
    """
    return: None (정상) or dict(policy_response_fields...)

    CRISIS(자해/자살)와 PRIVACY(개인정보 regex)만 즉시 차단.
    나머지(성적/혐오/범죄/정치/종교)는 LLM이 프롬프트 가이드에 따라 자연스럽게 처리.
    """
    hit = moderate_text(db, text_for_check)
    if not hit:
        return None

    rule, _kw = hit  # rule: PolicyRule

    # CRISIS나 PRIVACY만 즉시 차단 (나머지는 LLM이 처리)
    if rule.action not in (Action.CRISIS, Action.PRIVACY):
        return None

    # GPT가 사노 스타일로 응답 생성
    msg, should_end = generate_policy_response(db, rule, user_text)

    return {
        "status": Status.fallback,
        "assistant_text": trim(msg, OUTPUT_LIMIT),
        "fallback_code": f"POLICY_{rule.category.upper()}",
        "policy_category": rule.category,
        "should_end": should_end,
    }


def build_prompt(user_text: str, persona: str | None, summary) -> str:
    persona = persona or "You are Psano."
    summary_text = summary_to_text(summary)
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary_text}\n"
        f"User: {user_text}\n"
        "Assistant:"
    )


def build_start_prompt(db: Session, *, persona: str | None, summary, topic_ctx: str, visitor_name: str = "") -> str:
    persona = (persona or "").strip()
    summary_text = summary_to_text(summary).strip()
    visitor_name = (visitor_name or "").strip()

    # DB에서 프롬프트 템플릿 로드
    template = get_prompt(db, "talk_start_prompt", "")

    if template:
        return template.format(
            persona=persona,
            values_summary=summary_text,
            topic_ctx=topic_ctx,
            visitor_name=visitor_name,
            output_limit=OUTPUT_LIMIT,
        )

    # fallback: 하드코딩 프롬프트
    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")
    if visitor_name:
        base.append(f"[visitor_name]\n{visitor_name}\n")
    base.append(topic_ctx)
    base.append(
        "너는 전시 작품 '사노'야.\n"
        f"규칙:\n- 한국어\n- {OUTPUT_LIMIT}자 이내\n"
        "- 첫 마디는 '대화를 여는 한 문장 + 짧은 질문 1개' 형태\n"
        "- persona_prompt의 SAFETY 규칙에 따라 민감 주제는 자연스럽게 처리\n"
        "- 관람객의 이름이 주어지면 가끔 친근하게 이름을 불러줘\n\n"
        "위 topic으로 대화를 시작하는 첫 마디를 만들어줘."
    )
    return "\n".join(base).strip()

def _format_recent_turns(rows) -> str:
    """
    rows: [{user_text, assistant_text}, ...] in chronological order
    """
    lines = []
    for r in rows:
        u = trim(r.get("user_text") or "", INPUT_LIMIT)
        a = trim(r.get("assistant_text") or "", OUTPUT_LIMIT)
        if u:
            lines.append(f"U: {u}")
        if a:
            lines.append(f"A: {a}")
    return "\n".join(lines).strip()


def _get_recent_turns(db: Session, session_id: int, limit_rows: int) -> str:
    """
    talk_messages에서 최근 limit_rows개를 가져와서 오래된 -> 최신 순서로 포맷.
    """
    rows = db.execute(
        text("""
            SELECT id, user_text, assistant_text
            FROM talk_messages
            WHERE session_id = :sid
            ORDER BY id DESC
            LIMIT :lim
        """),
        {"sid": session_id, "lim": int(limit_rows)},
    ).mappings().all()

    rows = list(rows or [])
    rows.reverse()  # 최신->과거로 뽑았으니 뒤집어서 과거->최신
    return _format_recent_turns(rows)


def build_turn_prompt(
    db: Session,
    *,
    persona: str | None,
    summary,
    topic_ctx: str,
    session_memory: str,
    recent_turns: str,
    user_text: str,
    visitor_name: str = "",
) -> str:
    persona = persona or "You are Psano."
    summary_text = summary_to_text(summary)
    visitor_name = (visitor_name or "").strip()

    mem = trim(session_memory or "", MEMORY_LIMIT)
    recent = (recent_turns or "").strip()

    # DB에서 프롬프트 템플릿 로드
    template = get_prompt(db, "talk_turn_prompt", "")

    if template:
        return template.format(
            persona=persona,
            values_summary=summary_text,
            topic_ctx=topic_ctx,
            session_memory=mem,
            recent_turns=recent,
            user_text=user_text,
            visitor_name=visitor_name,
            output_limit=OUTPUT_LIMIT,
            memory_limit=MEMORY_LIMIT,
        )

    # fallback: 하드코딩 프롬프트
    visitor_section = f"[visitor_name]\n{visitor_name}\n\n" if visitor_name else ""
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary_text}\n\n"
        f"{visitor_section}"
        f"{topic_ctx}\n"
        f"[session_memory]\n{mem}\n\n"
        f"[recent_turns]\n{recent}\n\n"
        "규칙:\n"
        f"- ASSISTANT는 {OUTPUT_LIMIT}자 이내\n"
        f"- MEMORY는 {MEMORY_LIMIT}자 이내\n"
        "- MEMORY는 '세션에서 앞으로 기억할 핵심'만 압축해서 최신 버전으로 작성(중복 줄이기)\n"
        "- persona_prompt의 SAFETY 규칙에 따라 민감 주제는 자연스럽게 처리\n"
        "- 관람객의 이름이 주어지면 가끔 친근하게 이름을 불러줘\n"
        "- 출력은 반드시 정확히 두 줄 형식으로만:\n"
        "ASSISTANT: ...\n"
        "MEMORY: ...\n\n"
        f"User: {user_text}\n"
    ).strip()


def _parse_assistant_and_memory(raw: str) -> tuple[str, str]:
    """
    모델 출력에서 ASSISTANT/MEMORY 두 줄을 파싱.
    실패하면 assistant에 raw 전체를 넣고 memory는 빈 문자열.
    """
    raw = (raw or "").strip()
    if not raw:
        return "", ""

    assistant = ""
    memory = ""

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("ASSISTANT:"):
            assistant = ln[len("ASSISTANT:") :].strip()
        elif ln.startswith("MEMORY:"):
            memory = ln[len("MEMORY:") :].strip()

    if not assistant:
        assistant = raw

    return trim(assistant, OUTPUT_LIMIT), trim(memory, MEMORY_LIMIT)


def _update_session_memory_and_count(db: Session, session_id: int, memory: str):
    """sessions.talk_memory / turn_count 업데이트"""
    db.execute(
        text("""
            UPDATE sessions
            SET talk_memory = :mem,
                turn_count = COALESCE(turn_count, 0) + 1
            WHERE id = :sid
        """),
        {"sid": session_id, "mem": trim(memory or "", MEMORY_LIMIT)},
    )
    db.commit()

@router.post("/start", response_model=TalkStartResponse)
def talk_start(req: TalkStartRequest, db: Session = Depends(get_db)):
    # 1) psano_state 읽기
    st = db.execute(
        text(
            """
            SELECT phase, persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
            """
        )
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # 인격 형성 이후에만 허용
    if st["phase"] != "talk":
        raise HTTPException(status_code=409, detail="phase is not talk")

    # 2) 세션 체크 + (A) talk 최초 시작 시에만 세션 talk 필드 초기화/고정
    sess = db.execute(
        text(
            """
            SELECT id, ended_at, topic_id, talk_memory, turn_count, visitor_name
            FROM sessions
            WHERE id = :sid
            """
        ),
        {"sid": req.session_id},
    ).mappings().first()

    if not sess:
        raise HTTPException(status_code=404, detail="session not found")

    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 이미 talk 시작된 세션이면 topic 불일치 컷
    if sess.get("topic_id") is not None and int(sess["topic_id"]) != int(req.topic_id):
        raise HTTPException(status_code=409, detail="topic mismatch for this session")

    # talk 시작 최초 1회만 초기화
    if sess.get("topic_id") is None:
        db.execute(
            text("""
                UPDATE sessions
                SET topic_id = :tid, talk_memory = '', turn_count = 0
                WHERE id = :sid
            """),
            {"sid": req.session_id, "tid": int(req.topic_id)},
        )
        db.commit()

    # 3) topic 로드
    topic_ctx = _topic_context(db, req.topic_id)

    # 4) 프롬프트 구성 (DB에서 템플릿 로드)
    prompt = build_start_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        topic_ctx=topic_ctx,
        visitor_name=sess.get("visitor_name") or "",
    )

    # 5) LLM 호출 (공통 래퍼: timeout 8초, retry 2회)
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
        model=getattr(req, "model", None),
        max_tokens=getattr(req, "max_output_tokens", None) or 1000,  # GPT-5 reasoning 모델은 더 많은 토큰 필요
        fallback_text=fallback_text,
    )

    if result.success:
        status = Status.ok
        assistant_first_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = None
    else:
        status = Status.fallback
        assistant_first_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = result.fallback_code

    # start는 저장 안 함
    return {
        "status": status,
        "assistant_first_text": assistant_first_text,
        "fallback_code": fallback_code,
    }


@router.post("/turn", response_model=TalkResponse)
def talk_turn(req: TalkRequest, db: Session = Depends(get_db)):
    # 0) topic_id 필수 가드
    if getattr(req, "topic_id", None) in (None, "", 0):
        raise HTTPException(status_code=400, detail="topic_id is required")

    # 1) psano_state 읽기
    st = db.execute(
        text(
            """
            SELECT phase, persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
            """
        )
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # 인격 형성 이후에만 허용
    if st["phase"] != "talk":
        raise HTTPException(status_code=409, detail="phase is not talk")

    # 2) 세션 체크 (B 포함)
    sess = db.execute(
        text(
            """
            SELECT id, ended_at, topic_id, talk_memory, turn_count, visitor_name
            FROM sessions
            WHERE id = :sid
            """
        ),
        {"sid": req.session_id},
    ).mappings().first()

    if not sess:
        raise HTTPException(status_code=404, detail="session not found")

    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # (B) start 안 했으면 turn 불가
    if sess.get("topic_id") is None:
        raise HTTPException(
            status_code=409,
            detail="talk not started for this session. call POST /talk/start first.",
        )

    # topic 불일치 컷
    if int(sess["topic_id"]) != int(req.topic_id):
        raise HTTPException(status_code=409, detail="topic mismatch for this session")

    # 2.5) 입력 길이 제한
    user_text = trim(req.user_text, INPUT_LIMIT)

    # 2.6) topic 컨텍스트
    topic_ctx = _topic_context(db, req.topic_id) + "\n"

    # 2.7) 정책 필터(토픽+유저 같이 검사)
    policy_check_text = (topic_ctx + user_text).strip()
    policy = _apply_policy_guard(db, policy_check_text, user_text)
    if policy:
        assistant_text = policy["assistant_text"]
        fallback_code = policy["fallback_code"]

        # 로그 저장(talk_messages)
        db.execute(
            text("""
                INSERT INTO talk_messages (session_id, topic_id, user_text, assistant_text, status)
                VALUES (:sid, :tid, :u, :a, :s)
            """),
            {
                "sid": req.session_id,
                "tid": int(req.topic_id),
                "u": user_text,
                "a": assistant_text,
                "s": Status.fallback.value,
            },
        )
        db.commit()

        return {
            "status": Status.fallback,
            "ui_text": assistant_text,
            "fallback_code": fallback_code,
        }

    # 3) 세션 메모 + 최근 턴 로드(세션 범위)
    session_memory = trim(sess.get("talk_memory") or "", MEMORY_LIMIT)
    recent_turns = _get_recent_turns(db, req.session_id, RECENT_TURNS)

    # 4) 프롬프트 구성(대화형, DB에서 템플릿 로드)
    prompt = build_turn_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        topic_ctx=topic_ctx.strip(),
        session_memory=session_memory,
        recent_turns=recent_turns,
        user_text=user_text,
        visitor_name=sess.get("visitor_name") or "",
    )

    # 5) LLM 호출 (공통 래퍼: timeout 8초, retry 2회)
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
        model=getattr(req, "model", None),
        max_tokens=getattr(req, "max_output_tokens", None) or 1000,  # GPT-5 reasoning 모델은 더 많은 토큰 필요
        fallback_text="",  # 파싱 후 처리하므로 빈 문자열
    )

    new_memory = session_memory

    if result.success:
        assistant_text, parsed_memory = _parse_assistant_and_memory(result.content)
        if not assistant_text:
            # 파싱 실패 시 fallback
            status = Status.fallback
            fallback_code = "LLM_PARSE_ERROR"
            assistant_text = trim(fallback_text, OUTPUT_LIMIT)
        else:
            status = Status.ok
            fallback_code = None
            if parsed_memory:
                new_memory = trim(parsed_memory, MEMORY_LIMIT)
    else:
        status = Status.fallback
        fallback_code = result.fallback_code
        assistant_text = trim(fallback_text, OUTPUT_LIMIT)

    # 6) DB 저장 talk_messages
    db.execute(
        text("""
            INSERT INTO talk_messages (session_id, topic_id, user_text, assistant_text, status)
            VALUES (:sid, :tid, :u, :a, :s)
        """),
        {
            "sid": req.session_id,
            "tid": int(req.topic_id),
            "u": user_text,
            "a": assistant_text,
            "s": status.value,
        },
    )
    db.commit()

    # 7) 세션 메모/턴카운트 업데이트
    _update_session_memory_and_count(db, req.session_id, new_memory)

    return {
        "status": status,
        "ui_text": assistant_text,
        "fallback_code": fallback_code,
    }


@router.post("/end", response_model=TalkEndResponse)
def talk_end(req: TalkEndRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    return end_session_core(db, sid, "talk_end")

@router.get("/topics", response_model=TopicsResponse)
def get_chat_topics(db: Session = Depends(get_db)):
    try:
        rows = db.execute(
            text(
                """
                SELECT id, title, description, created_at
                FROM talk_topics
                ORDER BY id ASC
                """
            )
        ).mappings().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    topics = []
    for r in rows:
        topics.append(
            {
                "id": int(r["id"]),
                "title": r["title"],
                "description": r["description"],
                "created_at": iso(r.get("created_at")),
            }
        )
    return {"topics": topics}


# =========================
# Idle Talk (혼잣말 기반 대화)
# =========================


def _load_idle(db: Session, idle_id: int):
    """idle 혼잣말 로드"""
    return db.execute(
        text("""
            SELECT id, axis_key, question_text, value
            FROM psano_idle
            WHERE id = :id AND enable = 1
        """),
        {"id": idle_id}
    ).mappings().first()


def _idle_context(db: Session, idle_id: int) -> tuple[str, str]:
    """idle 컨텍스트 반환: (context_str, monologue_text)"""
    idle = _load_idle(db, idle_id)
    if not idle:
        raise HTTPException(status_code=404, detail=f"Idle monologue not found: {idle_id}")
    monologue = (idle.get("question_text") or "").strip()
    axis_key = (idle.get("axis_key") or "").strip()
    ctx = f"[idle_monologue]\n- axis: {axis_key}\n- text: {monologue}\n"
    return ctx, monologue


def _build_idle_start_prompt(db: Session, *, persona: str | None, summary, idle_ctx: str, visitor_name: str = "") -> str:
    """idle-talk 시작 프롬프트 생성"""
    persona = (persona or "").strip()
    summary_text = summary_to_text(summary).strip()
    visitor_name = (visitor_name or "").strip()

    template = get_prompt(db, "idle_talk_start_prompt", "")

    if template:
        return template.format(
            persona=persona,
            values_summary=summary_text,
            idle_ctx=idle_ctx,
            visitor_name=visitor_name,
            output_limit=OUTPUT_LIMIT,
        )

    # fallback: 하드코딩 프롬프트
    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")
    if visitor_name:
        base.append(f"[visitor_name]\n{visitor_name}\n")
    base.append(idle_ctx)
    base.append(
        "너는 전시 작품 '사노'야.\n"
        f"규칙:\n- 한국어\n- {OUTPUT_LIMIT}자 이내\n"
        "- 위 혼잣말을 말한 후, 관람객이 다가왔어. 자연스럽게 대화를 시작해.\n"
        "- 혼잣말 내용과 연결되는 짧은 인사 + 질문 1개 형태로 말해.\n"
        "- persona_prompt의 SAFETY 규칙에 따라 민감 주제는 자연스럽게 처리\n"
        "- 관람객의 이름이 주어지면 가끔 친근하게 이름을 불러줘\n\n"
        "관람객에게 건네는 첫 마디를 만들어줘."
    )
    return "\n".join(base).strip()


def _get_recent_idle_turns(db: Session, session_id: int, limit_rows: int) -> str:
    """idle_talk_messages에서 최근 턴 로드"""
    rows = db.execute(
        text("""
            SELECT id, user_text, assistant_text
            FROM idle_talk_messages
            WHERE session_id = :sid
            ORDER BY id DESC
            LIMIT :lim
        """),
        {"sid": session_id, "lim": int(limit_rows)},
    ).mappings().all()

    rows = list(rows or [])
    rows.reverse()
    return _format_recent_turns(rows)


def _build_idle_turn_prompt(
    db: Session,
    *,
    persona: str | None,
    summary,
    idle_ctx: str,
    session_memory: str,
    recent_turns: str,
    user_text: str,
    visitor_name: str = "",
) -> str:
    """idle-talk 턴 프롬프트 생성"""
    persona = persona or "You are Psano."
    summary_text = summary_to_text(summary)
    visitor_name = (visitor_name or "").strip()

    mem = trim(session_memory or "", MEMORY_LIMIT)
    recent = (recent_turns or "").strip()

    template = get_prompt(db, "idle_talk_turn_prompt", "")

    if template:
        return template.format(
            persona=persona,
            values_summary=summary_text,
            idle_ctx=idle_ctx,
            session_memory=mem,
            recent_turns=recent,
            user_text=user_text,
            visitor_name=visitor_name,
            output_limit=OUTPUT_LIMIT,
            memory_limit=MEMORY_LIMIT,
        )

    # fallback: 하드코딩 프롬프트
    visitor_section = f"[visitor_name]\n{visitor_name}\n\n" if visitor_name else ""
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary_text}\n\n"
        f"{visitor_section}"
        f"{idle_ctx}\n"
        f"[session_memory]\n{mem}\n\n"
        f"[recent_turns]\n{recent}\n\n"
        "규칙:\n"
        f"- ASSISTANT는 {OUTPUT_LIMIT}자 이내\n"
        f"- MEMORY는 {MEMORY_LIMIT}자 이내\n"
        "- MEMORY는 '세션에서 앞으로 기억할 핵심'만 압축해서 최신 버전으로 작성(중복 줄이기)\n"
        "- persona_prompt의 SAFETY 규칙에 따라 민감 주제는 자연스럽게 처리\n"
        "- 관람객의 이름이 주어지면 가끔 친근하게 이름을 불러줘\n"
        "- 출력은 반드시 정확히 두 줄 형식으로만:\n"
        "ASSISTANT: ...\n"
        "MEMORY: ...\n\n"
        f"User: {user_text}\n"
    ).strip()


def _update_idle_session_memory(db: Session, session_id: int, memory: str):
    """sessions.idle_talk_memory / idle_turn_count 업데이트"""
    db.execute(
        text("""
            UPDATE sessions
            SET idle_talk_memory = :mem,
                idle_turn_count = COALESCE(idle_turn_count, 0) + 1
            WHERE id = :sid
        """),
        {"sid": session_id, "mem": trim(memory or "", MEMORY_LIMIT)},
    )
    db.commit()


@router.post("/idle/start", response_model=IdleTalkStartResponse)
def idle_talk_start(req: IdleTalkStartRequest, db: Session = Depends(get_db)):
    """
    POST /talk/idle/start
    혼잣말 기반 대화 시작
    """
    # 1) psano_state 읽기
    st = db.execute(
        text("""
            SELECT phase, persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # 2) 세션 체크
    sess = db.execute(
        text("""
            SELECT id, ended_at, idle_id, idle_talk_memory, idle_turn_count, visitor_name
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": req.session_id},
    ).mappings().first()

    if not sess:
        raise HTTPException(status_code=404, detail="session not found")

    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 이미 idle-talk 시작된 세션이면 idle 불일치 컷
    if sess.get("idle_id") is not None and int(sess["idle_id"]) != int(req.idle_id):
        raise HTTPException(status_code=409, detail="idle mismatch for this session")

    # idle-talk 최초 1회만 초기화
    if sess.get("idle_id") is None:
        db.execute(
            text("""
                UPDATE sessions
                SET idle_id = :iid, idle_talk_memory = '', idle_turn_count = 0
                WHERE id = :sid
            """),
            {"sid": req.session_id, "iid": int(req.idle_id)},
        )
        db.commit()

    # 3) idle 컨텍스트 로드
    idle_ctx, monologue_text = _idle_context(db, req.idle_id)

    # 4) 프롬프트 구성
    prompt = _build_idle_start_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        idle_ctx=idle_ctx,
        visitor_name=sess.get("visitor_name") or "",
    )

    # 5) LLM 호출
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
        model=getattr(req, "model", None),
        max_tokens=getattr(req, "max_output_tokens", None) or 1000,
        fallback_text=fallback_text,
    )

    if result.success:
        status = Status.ok
        assistant_first_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = None
    else:
        status = Status.fallback
        assistant_first_text = trim(result.content, OUTPUT_LIMIT)
        fallback_code = result.fallback_code

    return {
        "status": status,
        "assistant_first_text": assistant_first_text,
        "idle_text": monologue_text,
        "fallback_code": fallback_code,
    }


@router.post("/idle/turn", response_model=IdleTalkTurnResponse)
def idle_talk_turn(req: IdleTalkTurnRequest, db: Session = Depends(get_db)):
    """
    POST /talk/idle/turn
    혼잣말 기반 대화 턴
    """
    # 1) psano_state 읽기
    st = db.execute(
        text("""
            SELECT phase, persona_prompt, values_summary
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # 2) 세션 체크
    sess = db.execute(
        text("""
            SELECT id, ended_at, idle_id, idle_talk_memory, idle_turn_count, visitor_name
            FROM sessions
            WHERE id = :sid
        """),
        {"sid": req.session_id},
    ).mappings().first()

    if not sess:
        raise HTTPException(status_code=404, detail="session not found")

    if sess.get("ended_at") is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # idle-talk 시작 안 했으면 turn 불가
    if sess.get("idle_id") is None:
        raise HTTPException(
            status_code=409,
            detail="idle-talk not started for this session. call POST /talk/idle/start first.",
        )

    # 3) 입력 길이 제한
    user_text = trim(req.user_text, INPUT_LIMIT)

    # 4) idle 컨텍스트 로드
    idle_ctx, _ = _idle_context(db, int(sess["idle_id"]))

    # 5) 정책 필터
    policy_check_text = (idle_ctx + user_text).strip()
    policy = _apply_policy_guard(db, policy_check_text, user_text)
    if policy:
        # 로그 저장
        db.execute(
            text("""
                INSERT INTO idle_talk_messages (session_id, idle_id, user_text, assistant_text, status)
                VALUES (:sid, :iid, :u, :a, :s)
            """),
            {
                "sid": req.session_id,
                "iid": int(sess["idle_id"]),
                "u": user_text,
                "a": policy["assistant_text"],
                "s": Status.fallback.value,
            },
        )
        db.commit()

        return {
            "status": Status.fallback,
            "ui_text": policy["assistant_text"],
            "fallback_code": policy["fallback_code"],
            "policy_category": policy.get("policy_category"),
            "should_end": policy.get("should_end", False),
        }

    # 6) 세션 메모 + 최근 턴 로드
    session_memory = trim(sess.get("idle_talk_memory") or "", MEMORY_LIMIT)
    recent_turns = _get_recent_idle_turns(db, req.session_id, RECENT_TURNS)

    # 7) 프롬프트 구성
    prompt = _build_idle_turn_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        idle_ctx=idle_ctx.strip(),
        session_memory=session_memory,
        recent_turns=recent_turns,
        user_text=user_text,
        visitor_name=sess.get("visitor_name") or "",
    )

    # 8) LLM 호출
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
        model=getattr(req, "model", None),
        max_tokens=getattr(req, "max_output_tokens", None) or 1000,
        fallback_text="",
    )

    new_memory = session_memory

    if result.success:
        assistant_text, parsed_memory = _parse_assistant_and_memory(result.content)
        if not assistant_text:
            status = Status.fallback
            fallback_code = "LLM_PARSE_ERROR"
            assistant_text = trim(fallback_text, OUTPUT_LIMIT)
        else:
            status = Status.ok
            fallback_code = None
            if parsed_memory:
                new_memory = trim(parsed_memory, MEMORY_LIMIT)
    else:
        status = Status.fallback
        fallback_code = result.fallback_code
        assistant_text = trim(fallback_text, OUTPUT_LIMIT)

    # 9) DB 저장
    db.execute(
        text("""
            INSERT INTO idle_talk_messages (session_id, idle_id, user_text, assistant_text, status)
            VALUES (:sid, :iid, :u, :a, :s)
        """),
        {
            "sid": req.session_id,
            "iid": int(sess["idle_id"]),
            "u": user_text,
            "a": assistant_text,
            "s": status.value,
        },
    )
    db.commit()

    # 10) 세션 메모/턴카운트 업데이트
    _update_idle_session_memory(db, req.session_id, new_memory)

    return {
        "status": status,
        "ui_text": assistant_text,
        "fallback_code": fallback_code,
    }
