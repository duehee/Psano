import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.session_service import end_session_core
from util.utils import trim, summary_to_text, get_prompt, get_config
from util.constants import (
    DEFAULT_GLOBAL_TURN_MAX, DEFAULT_GLOBAL_WARNING_START,
    TALK_INPUT_LIMIT, TALK_MEMORY_LIMIT, TALK_RECENT_TURNS
)
import random
import json
import re

from schemas.talk import (
    TalkStartRequest,
    TalkStartResponse,
    TalkTurnRequest,
    TalkTurnResponse,
    TalkEndRequest,
    TalkEndResponse,
)

from schemas.common import Status
from database import get_db
from services.llm_service import call_llm
from util.talk_utils import get_policy_guide, OUTPUT_LIMIT
from routers._store import LOCK, SESSIONS

# constants에서 import한 값 사용 (하위 호환성을 위한 별칭)
INPUT_LIMIT = TALK_INPUT_LIMIT
MEMORY_LIMIT = TALK_MEMORY_LIMIT
RECENT_TURNS = TALK_RECENT_TURNS

router = APIRouter()

# 하드코딩 fallback (DB에 없을 때 기본값)
_DEFAULT_FALLBACK_LINES = [
    "지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.",
    "나는 아직 정리 중이야. 너의 질문이 물결처럼 남아 있어.",
    "답을 급히 만들고 싶진 않아. 한 번만 더 천천히 말해줄래?",
]


def _get_fallback_lines(db: Session) -> list:
    """DB에서 fallback 메시지 로드 (없으면 기본값)"""
    return get_config(db, "talk_fallback_lines", _DEFAULT_FALLBACK_LINES)


def _safe_format(template: str, **kwargs) -> str:
    """
    .format() 대신 수동 replace. {key}만 치환하고 JSON의 {...}는 그대로 둠.
    """
    result = template
    for key, value in kwargs.items():
        result = result.replace("{" + key + "}", str(value))
    return result


# =========================
# Idle 관련 헬퍼 함수
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
    idle_talk_messages에서 최근 limit_rows개를 가져와서 오래된 -> 최신 순서로 포맷.
    """
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


# =========================
# 프롬프트 빌더
# =========================

def _build_start_prompt(db: Session, *, persona: str | None, summary, idle_ctx: str, visitor_name: str = "") -> str:
    """대화 시작 프롬프트 생성"""
    persona = (persona or "").strip()
    summary_text = summary_to_text(summary).strip()
    visitor_name = (visitor_name or "").strip()

    template = get_prompt(db, "talk_start_prompt", "")

    if template:
        return _safe_format(
            template,
            persona=persona,
            values_summary=summary_text,
            topic_ctx=idle_ctx,  # idle_ctx를 topic_ctx 자리에
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


def _build_turn_prompt(
    db: Session,
    *,
    persona: str | None,
    summary,
    idle_ctx: str,
    session_memory: str,
    recent_turns: str,
    user_text: str,
    visitor_name: str = "",
    policy_guide: str | None = None,
    local_warning: str | None = None,
    ask_continue: bool = False,
) -> str:
    """대화 턴 프롬프트 생성"""
    persona = persona or "You are Psano."
    summary_text = summary_to_text(summary)
    visitor_name = (visitor_name or "").strip()
    policy_section = f"\n{policy_guide}\n" if policy_guide else ""
    local_warning_section = f"\n{local_warning}\n" if local_warning else ""
    ask_continue_section = ""
    if ask_continue:
        ask_continue_section = """
[대화 지속 확인]
이번 응답 끝에 관람객에게 대화를 계속할 의향이 있는지 자연스럽게 물어보세요.
예시: "...더 이야기해볼까?", "...계속 나눠볼래?", "...여기서 멈출까, 아니면 더?"
- 강요하지 말고 부드럽게
- 사노의 말투를 유지하면서
"""

    mem = trim(session_memory or "", MEMORY_LIMIT)
    recent = (recent_turns or "").strip()

    template = get_prompt(db, "talk_turn_prompt", "")

    if template:
        return _safe_format(
            template,
            persona=persona,
            values_summary=summary_text,
            topic_ctx=idle_ctx,  # idle_ctx를 topic_ctx 자리에
            session_memory=mem,
            recent_turns=recent,
            user_text=user_text,
            visitor_name=visitor_name,
            output_limit=OUTPUT_LIMIT,
            memory_limit=MEMORY_LIMIT,
            policy_guide=policy_section,
            local_warning=local_warning_section,
            ask_continue=ask_continue_section,
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
        f"{policy_section}"
        f"{local_warning_section}"
        f"{ask_continue_section}"
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
    모델 출력에서 ASSISTANT/MEMORY 파싱.
    지원 형식:
    1. ASSISTANT: ... / MEMORY: ... (기존)
    2. JSON: {"assistant": "...", "memory": "..."} (백틱 포함 가능)
    """
    raw = (raw or "").strip()
    if not raw:
        return "", ""

    assistant = ""
    memory = ""

    # 1) JSON 형식 시도 (백틱 제거)
    json_text = raw
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw, re.DOTALL)
    if json_match:
        json_text = json_match.group(1).strip()

    try:
        data = json.loads(json_text)
        if isinstance(data, dict):
            assistant = data.get("assistant") or data.get("assistant_text") or ""
            memory = data.get("memory") or ""
            if assistant:
                return trim(assistant, OUTPUT_LIMIT), trim(memory, MEMORY_LIMIT)
    except (json.JSONDecodeError, TypeError):
        pass

    # 2) 기존 ASSISTANT: / MEMORY: 형식
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    for ln in lines:
        if ln.startswith("ASSISTANT:"):
            assistant = ln[len("ASSISTANT:"):].strip()
        elif ln.startswith("MEMORY:"):
            memory = ln[len("MEMORY:"):].strip()

    if not assistant:
        assistant = raw

    return trim(assistant, OUTPUT_LIMIT), trim(memory, MEMORY_LIMIT)


def _update_session_memory(db: Session, session_id: int, memory: str):
    """sessions.idle_talk_memory / idle_turn_count 업데이트"""
    mem_trimmed = trim(memory or "", MEMORY_LIMIT)
    db.execute(
        text("""
            UPDATE sessions
            SET idle_talk_memory = :mem,
                idle_turn_count = COALESCE(idle_turn_count, 0) + 1
            WHERE id = :sid
        """),
        {"sid": session_id, "mem": mem_trimmed},
    )
    db.commit()

    # 메모리 캐시 동기화
    with LOCK:
        sess = SESSIONS.get(session_id)
        if sess:
            sess["idle_talk_memory"] = mem_trimmed
            sess["idle_turn_count"] = (sess.get("idle_turn_count") or 0) + 1


# =========================
# API 엔드포인트
# =========================

@router.post("/start", response_model=TalkStartResponse)
def talk_start(req: TalkStartRequest, db: Session = Depends(get_db)):
    """
    POST /talk/start
    idle 혼잣말 기반 대화 시작
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

    # 이미 talk 시작된 세션이면 idle 불일치 컷
    if sess.get("idle_id") is not None and int(sess["idle_id"]) != int(req.idle_id):
        raise HTTPException(status_code=409, detail="idle mismatch for this session")

    # talk 최초 1회만 초기화
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

        # 메모리 캐시 동기화
        with LOCK:
            cached_sess = SESSIONS.get(req.session_id)
            if cached_sess:
                cached_sess["idle_id"] = int(req.idle_id)
                cached_sess["idle_talk_memory"] = ""
                cached_sess["idle_turn_count"] = 0

    # 3) idle 컨텍스트 로드
    idle_ctx, monologue_text = _idle_context(db, req.idle_id)

    # 4) 프롬프트 구성
    prompt = _build_start_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        idle_ctx=idle_ctx,
        visitor_name=sess.get("visitor_name") or "",
    )

    # 5) LLM 호출
    fallback_lines = _get_fallback_lines(db)
    fallback_text = fallback_lines[int(time.time()) % len(fallback_lines)]
    result = call_llm(
        prompt,
        db=db,
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

    # 이벤트 로깅
    from util.utils import log_event
    log_event("talk_start", session_id=req.session_id, idle_id=req.idle_id)

    return {
        "status": status,
        "assistant_first_text": assistant_first_text,
        "idle_text": monologue_text,
        "fallback_code": fallback_code,
    }


@router.get("/start", response_model=TalkStartResponse)
def talk_start_get(session_id: int, idle_id: int, db: Session = Depends(get_db)):
    """TD용 GET 엔드포인트 - Query 파라미터로 대화 시작"""
    req = TalkStartRequest(session_id=session_id, idle_id=idle_id)
    return talk_start(req, db)


@router.post("/turn", response_model=TalkTurnResponse)
def talk_turn(req: TalkTurnRequest, db: Session = Depends(get_db)):
    """
    POST /talk/turn
    idle 혼잣말 기반 대화 턴
    """
    # 1) psano_state 읽기 (글로벌 턴 카운트 포함)
    st = db.execute(
        text("""
            SELECT phase, persona_prompt, values_summary, global_turn_count
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    # 글로벌 설정 로드
    global_turn_max = get_config(db, "global_turn_max", DEFAULT_GLOBAL_TURN_MAX)
    global_warning_start = get_config(db, "global_warning_start", DEFAULT_GLOBAL_WARNING_START)
    global_turn_count = int(st.get("global_turn_count") or 0)

    # 2) 글로벌 엔딩 체크 (365 도달)
    if global_turn_count >= global_turn_max:
        global_ending_msg = get_config(db, "global_ending_message", "여기까지야.")
        # 이벤트 로깅
        from util.utils import log_event
        log_event("global_ending", turn_count=global_turn_count, turn_max=global_turn_max)
        return {
            "status": Status.ok,
            "ui_text": global_ending_msg,
            "fallback_code": None,
            "policy_category": None,
            "should_end": True,
            "warning_text": None,
            "global_ended": True,
        }

    # 3) 예고 구간 체크 (355~364)
    warning_text = None
    if global_turn_count >= global_warning_start:
        try:
            warning_messages_raw = get_config(db, "global_warning_messages", None)
            if warning_messages_raw:
                if isinstance(warning_messages_raw, str):
                    warning_messages = json.loads(warning_messages_raw)
                else:
                    warning_messages = warning_messages_raw
                warning_text = random.choice(warning_messages)
        except Exception:
            warning_text = "이제 시간이 거의 다 되어가는 것 같아."

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

    # talk 시작 안 했으면 turn 불가
    if sess.get("idle_id") is None:
        raise HTTPException(
            status_code=409,
            detail="talk not started for this session. call POST /talk/start first.",
        )

    # 2.5) 로컬 엔딩 체크
    idle_turn_count = int(sess.get("idle_turn_count") or 0)
    local_end_turn_count = get_config(db, "local_end_turn_count", 50)
    local_warning_threshold = get_config(db, "local_warning_threshold", 5)
    remaining_turns = local_end_turn_count - idle_turn_count

    # 로컬 토큰 소진 → 즉시 종료 (엔딩 멘트 없음)
    if remaining_turns <= 0:
        return {
            "status": Status.ok,
            "ui_text": "",
            "fallback_code": None,
            "policy_category": None,
            "should_end": True,
            "warning_text": None,
            "global_ended": False,
        }

    # 로컬 예고 (잔여 ≤ threshold)
    local_warning = None
    if remaining_turns <= local_warning_threshold:
        local_warning = f"""[세션 종료 임박]
이 대화가 곧 끝나갑니다. (잔여: {remaining_turns}턴)
자연스럽게 마무리 어조를 사용하세요:
- "이쯤에서", "여기까지", "지금쯤이면" 등의 표현
- 대화를 정리하는 듯한 톤
- 급하게 끝내지 말고 자연스럽게"""

    # N턴마다 "더 할래?" 질문 트리거
    local_ask_interval = get_config(db, "local_ask_interval", 10)
    ask_continue = (idle_turn_count > 0 and idle_turn_count % local_ask_interval == 0)

    # 3) 입력 길이 제한
    user_text = trim(req.user_text, INPUT_LIMIT)

    # 4) idle 컨텍스트 로드
    idle_ctx, _ = _idle_context(db, int(sess["idle_id"]))

    # 5) 정책 가이드 확인 (매칭 시 LLM 프롬프트에 주입)
    policy_guide, policy_category = get_policy_guide(db, user_text)

    # 6) 세션 메모 + 최근 턴 로드
    session_memory = trim(sess.get("idle_talk_memory") or "", MEMORY_LIMIT)
    recent_turns = _get_recent_turns(db, req.session_id, RECENT_TURNS)

    # 7) 프롬프트 구성
    prompt = _build_turn_prompt(
        db,
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        idle_ctx=idle_ctx.strip(),
        session_memory=session_memory,
        recent_turns=recent_turns,
        user_text=user_text,
        visitor_name=sess.get("visitor_name") or "",
        policy_guide=policy_guide,
        local_warning=local_warning,
        ask_continue=ask_continue,
    )

    # 8) LLM 호출
    fallback_lines = _get_fallback_lines(db)
    fallback_text = fallback_lines[int(time.time()) % len(fallback_lines)]
    result = call_llm(
        prompt,
        db=db,
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
    _update_session_memory(db, req.session_id, new_memory)

    # 11) 글로벌 턴 카운트 증가
    db.execute(
        text("""
            UPDATE psano_state
            SET global_turn_count = COALESCE(global_turn_count, 0) + 1
            WHERE id = 1
        """)
    )
    db.commit()

    # 이번 턴 후 잔여 턴 (턴카운트가 방금 +1 됨)
    should_end = (remaining_turns - 1) <= 0

    return {
        "status": status,
        "ui_text": assistant_text,
        "fallback_code": fallback_code,
        "policy_category": policy_category,
        "should_end": should_end,
        "warning_text": warning_text,
        "global_ended": False,
    }


@router.get("/turn", response_model=TalkTurnResponse)
def talk_turn_get(session_id: int, user_text: str, db: Session = Depends(get_db)):
    """TD용 GET 엔드포인트 - Query 파라미터로 대화 턴"""
    req = TalkTurnRequest(session_id=session_id, user_text=user_text)
    return talk_turn(req, db)


@router.post("/end", response_model=TalkEndResponse)
def talk_end(req: TalkEndRequest, db: Session = Depends(get_db)):
    """
    POST /talk/end
    대화 종료
    """
    sid = int(req.session_id)
    return end_session_core(db, sid, "talk_end")


@router.get("/end", response_model=TalkEndResponse)
def talk_end_get(session_id: int, db: Session = Depends(get_db)):
    """TD용 GET 엔드포인트 - Query 파라미터로 대화 종료"""
    return end_session_core(db, session_id, "talk_end")