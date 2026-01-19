import time
import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from services.session_service import end_session_core

from schemas.talk import (
    TalkRequest,
    TalkResponse,
    TopicsResponse,
    TalkStartRequest,
    TalkStartResponse,
    TalkEndRequest,
    TalkEndResponse,
)

from schemas.common import Status
from routers.talk_policy import moderate_text, Action
from database import get_db
from openai import OpenAI

INPUT_LIMIT = 200
OUTPUT_LIMIT = 150

# 세션 메모(요약 기억) 최대 길이
MEMORY_LIMIT = 600

# 최근 턴 몇 개를 넣을지 (talk_messages 한 행 = 1턴)
RECENT_TURNS = 3

client = OpenAI()
router = APIRouter()

FALLBACK_LINES = [
    "지금은 말이 잘 나오지 않아. 조금 더 조용히 생각해볼게.",
    "나는 아직 정리 중이야. 너의 질문이 물결처럼 남아 있어.",
    "답을 급히 만들고 싶진 않아. 한 번만 더 천천히 말해줄래?",
]


def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)

def now_kst_naive() -> datetime:

    return datetime.utcnow() + timedelta(hours=9)

def _trim(s: str, n: int) -> str:
    s = (s or "").strip()
    return s[:n] if len(s) > n else s

def _summary_to_text(v) -> str:
    """values_summary가 JSON 컬럼이면 dict로 올 수도 있고,
    TEXT 컬럼이면 str로 올 수도 있어서 둘 다 안전 처리.
    """
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, ensure_ascii=False)
        except Exception:
            return str(v)
    return str(v)

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


def _policy_message(action: Action) -> tuple[str, bool]:
    """return: (assistant_text, should_end)
    - should_end는 UI에서 session end를 유도하고 싶을 때 쓰는 플래그
    """
    if action == Action.REDIRECT:
        return ("그 얘긴 잠깐 옆에 두고, 전시에서 가장 먼저 떠오른 장면 하나만 말해줄래?", False)
    if action == Action.WARN_END:
        return ("그런 표현은 여기선 같이 쓰기 어려워. 오늘 대화는 여기서 마칠게.", True)
    if action == Action.BLOCK:
        return ("그 주제는 여기선 다룰 수 없어. 대신 전시에서 느낀 감정 하나만 말해줄래?", False)
    if action == Action.PRIVACY:
        return ("개인정보(전화/주소/주민번호 등)는 말하지 말아줘. 대신 느낌이나 생각으로 말해줄래?", False)
    if action == Action.CRISIS:
        # OUTPUT_LIMIT 고려해서 짧게
        return ("지금 위험하면 112/119에 바로 연락해. 혼자 있지 말고 주변 사람에게 말해줘. 자살예방 109도 있어.", True)

    # fallback
    return (FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)], False)


def _apply_policy_guard(text_for_check: str):
    """return: None (정상) or dict(policy_response_fields...)"""
    hit = moderate_text(text_for_check)
    if not hit:
        return None
    rule, _kw = hit  # rule: PolicyRule
    msg, should_end = _policy_message(rule.action)

    # status는 fallback으로 통일
    return {
        "status": Status.fallback,
        "assistant_text": _trim(msg, OUTPUT_LIMIT),
        "fallback_code": getattr(rule.fallback_id, "value", str(rule.fallback_id)),
        "policy_category": rule.category,
        "should_end": should_end,
    }


def build_prompt(user_text: str, persona: str | None, summary) -> str:
    persona = persona or "You are Psano."
    summary_text = _summary_to_text(summary)
    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary_text}\n"
        f"User: {user_text}\n"
        "Assistant:"
    )


def build_start_prompt(*, persona: str | None, summary, topic_ctx: str) -> str:
    persona = (persona or "").strip()
    summary_text = _summary_to_text(summary).strip()

    base = []
    if persona:
        base.append(f"[persona_prompt]\n{persona}\n")
    if summary_text:
        base.append(f"[values_summary]\n{summary_text}\n")
    base.append(topic_ctx)
    base.append(
        "너는 전시 작품 '사노'야.\n"
        f"규칙:\n- 한국어\n- {OUTPUT_LIMIT}자 이내\n"
        "- 첫 마디는 '대화를 여는 한 문장 + 짧은 질문 1개' 형태\n"
        "- 과하게 길거나 위험한 주제는 피하고 안전하게\n\n"
        "위 topic으로 대화를 시작하는 첫 마디를 만들어줘."
    )
    return "\n".join(base).strip()

def _format_recent_turns(rows) -> str:
    """
    rows: [{user_text, assistant_text}, ...] in chronological order
    """
    lines = []
    for r in rows:
        u = _trim(r.get("user_text") or "", INPUT_LIMIT)
        a = _trim(r.get("assistant_text") or "", OUTPUT_LIMIT)
        if u:
            lines.append(f"U: {u}")
        if a:
            lines.append(f"A: {a}")
    return "\n".join(lines).strip()


def _get_recent_turns(db: Session, session_id: int, limit_rows: int) -> str:
    """
    talk_messages: 한 행이 한 턴(user_text + assistant_text)
    최근 limit_rows개를 가져와서 오래된 -> 최신 순서로 포맷.
    """
    rows = []
    try:
        rows = db.execute(
            text(
                f"""
                SELECT id, user_text, assistant_text
                FROM talk_messages
                WHERE session_id = :sid
                ORDER BY id DESC
                LIMIT {int(limit_rows)}
                """
            ),
            {"sid": session_id},
        ).mappings().all()
    except Exception:
        # id가 없거나 DB가 달라서 실패할 때 최소 호환(created_at 기준)
        try:
            rows = db.execute(
                text(
                    f"""
                    SELECT user_text, assistant_text
                    FROM talk_messages
                    WHERE session_id = :sid
                    ORDER BY created_at DESC
                    LIMIT {int(limit_rows)}
                    """
                ),
                {"sid": session_id},
            ).mappings().all()
        except Exception:
            rows = []

    rows = list(rows or [])
    rows.reverse()  # 최신->과거로 뽑았으니 뒤집어서 과거->최신
    return _format_recent_turns(rows)


def build_turn_prompt(
    *,
    persona: str | None,
    summary,
    topic_ctx: str,
    session_memory: str,
    recent_turns: str,
    user_text: str,
) -> str:
    persona = persona or "You are Psano."
    summary_text = _summary_to_text(summary)

    mem = _trim(session_memory or "", MEMORY_LIMIT)
    recent = (recent_turns or "").strip()

    return (
        f"{persona}\n"
        "Output language: Korean.\n"
        "Tone: philosophical/metaphorical, but avoid exaggerated emotions.\n"
        f"Values summary: {summary_text}\n\n"
        f"{topic_ctx}\n"
        f"[session_memory]\n{mem}\n\n"
        f"[recent_turns]\n{recent}\n\n"
        "규칙:\n"
        f"- ASSISTANT는 {OUTPUT_LIMIT}자 이내\n"
        f"- MEMORY는 {MEMORY_LIMIT}자 이내\n"
        "- MEMORY는 '세션에서 앞으로 기억할 핵심'만 압축해서 최신 버전으로 작성(중복 줄이기)\n"
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

    return _trim(assistant, OUTPUT_LIMIT), _trim(memory, MEMORY_LIMIT)


def _try_update_session_memory_and_count(db: Session, session_id: int, memory: str):
    """
    sessions.talk_memory / turn_count 업데이트.
    컬럼 없으면 조용히 무시.
    """
    try:
        db.execute(
            text(
                """
                UPDATE sessions
                SET talk_memory = :mem,
                    turn_count = COALESCE(turn_count, 0) + 1
                WHERE id = :sid
                """
            ),
            {"sid": session_id, "mem": _trim(memory or "", MEMORY_LIMIT)},
        )
        db.commit()
    except Exception:
        db.rollback()
        # 컬럼 없거나 제약 문제면 무시

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
            SELECT id, ended_at, topic_id, talk_memory, turn_count
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

    # talk 시작 최초 1회만 초기화(teach에서 만들어진 세션이라도 여기서만)
    if sess.get("topic_id") is None:
        try:
            db.execute(
                text(
                    """
                    UPDATE sessions
                    SET topic_id    = :tid,
                        talk_memory = '',
                        turn_count  = 0
                    WHERE id = :sid
                    """
                ),
                {"sid": req.session_id, "tid": int(req.topic_id)},
            )
            db.commit()
        except Exception:
            db.rollback()
            # 컬럼 없으면(마이그레이션 전) 그냥 통과

    # 3) topic 로드
    topic_ctx = _topic_context(db, req.topic_id)

    # 4) 프롬프트 구성
    prompt = build_start_prompt(
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        topic_ctx=topic_ctx,
    )

    # 5) GPT 호출 (실패하면 fallback)
    status = Status.ok
    fallback_code = None
    assistant_first_text = ""

    try:
        resp = client.chat.completions.create(
            model=getattr(req, "model", None) or "gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=getattr(req, "max_output_tokens", None) or 180,
        )
        assistant_first_text = _trim(resp.choices[0].message.content or "", OUTPUT_LIMIT)
        if not assistant_first_text:
            raise RuntimeError("empty output")
        status = Status.ok
    except Exception:
        status = Status.fallback
        fallback_code = "LLM_FAILED"
        assistant_first_text = _trim(
            FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)],
            OUTPUT_LIMIT,
        )

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
            SELECT id, ended_at, topic_id, talk_memory, turn_count
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
    user_text = _trim(req.user_text, INPUT_LIMIT)

    # 2.6) topic 컨텍스트
    topic_ctx = _topic_context(db, req.topic_id) + "\n"

    # 2.7) 정책 필터(토픽+유저 같이 검사)
    policy_check_text = (topic_ctx + user_text).strip()
    policy = _apply_policy_guard(policy_check_text)
    if policy:
        assistant_text = policy["assistant_text"]
        fallback_code = policy["fallback_code"]

        # 로그 저장(talk_messages) - topic_id 포함
        try:
            try:
                db.execute(
                    text(
                        """
                        INSERT INTO talk_messages (session_id, topic_id, user_text, assistant_text, status)
                        VALUES (:sid, :tid, :u, :a, :s)
                        """
                    ),
                    {
                        "sid": req.session_id,
                        "tid": int(req.topic_id),
                        "u": user_text,
                        "a": assistant_text,
                        "s": Status.fallback.value if hasattr(Status.fallback, "value") else str(Status.fallback),
                    },
                )
            except Exception:
                db.execute(
                    text(
                        """
                        INSERT INTO talk_messages (session_id, user_text, assistant_text, status)
                        VALUES (:sid, :u, :a, :s)
                        """
                    ),
                    {
                        "sid": req.session_id,
                        "u": user_text,
                        "a": assistant_text,
                        "s": Status.fallback.value if hasattr(Status.fallback, "value") else str(Status.fallback),
                    },
                )
            db.commit()
        except Exception:
            db.rollback()
            pass

        return {
            "status": Status.fallback,
            "ui_text": assistant_text,
            "fallback_code": fallback_code,
        }

    # 3) 세션 메모 + 최근 턴 로드(세션 범위)
    session_memory = _trim(sess.get("talk_memory") or "", MEMORY_LIMIT)
    recent_turns = _get_recent_turns(db, req.session_id, RECENT_TURNS)

    # 4) 프롬프트 구성(대화형)
    prompt = build_turn_prompt(
        persona=st.get("persona_prompt"),
        summary=st.get("values_summary"),
        topic_ctx=topic_ctx.strip(),
        session_memory=session_memory,
        recent_turns=recent_turns,
        user_text=user_text,
    )

    # 5) GPT 호출 (실패하면 fallback)
    status = Status.ok
    fallback_code = None
    assistant_text = ""
    new_memory = session_memory

    try:
        resp = client.chat.completions.create(
            model=getattr(req, "model", None) or "gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=getattr(req, "max_output_tokens", None) or 220,
        )

        raw = resp.choices[0].message.content or ""
        assistant_text, parsed_memory = _parse_assistant_and_memory(raw)

        if not assistant_text:
            raise RuntimeError("empty output")

        if parsed_memory:
            new_memory = _trim(parsed_memory, MEMORY_LIMIT)

        status = Status.ok

    except Exception:
        status = Status.fallback
        fallback_code = "LLM_FAILED"
        assistant_text = _trim(
            FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)],
            OUTPUT_LIMIT,
        )
        new_memory = session_memory

    # 6) DB 저장 talk_messages (topic_id 포함)
    try:
        try:
            db.execute(
                text(
                    """
                    INSERT INTO talk_messages (session_id, topic_id, user_text, assistant_text, status)
                    VALUES (:sid, :tid, :u, :a, :s)
                    """
                ),
                {
                    "sid": req.session_id,
                    "tid": int(req.topic_id),
                    "u": user_text,
                    "a": assistant_text,
                    "s": status.value if hasattr(status, "value") else str(status),
                },
            )
        except Exception:
            db.execute(
                text(
                    """
                    INSERT INTO talk_messages (session_id, user_text, assistant_text, status)
                    VALUES (:sid, :u, :a, :s)
                    """
                ),
                {
                    "sid": req.session_id,
                    "u": user_text,
                    "a": assistant_text,
                    "s": status.value if hasattr(status, "value") else str(status),
                },
            )
        db.commit()
    except Exception:
        db.rollback()
        pass

    # 7) 세션 메모/턴카운트 업데이트(가능하면)
    _try_update_session_memory_and_count(db, req.session_id, new_memory)

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
                "created_at": _iso(r.get("created_at")),
            }
        )
    return {"topics": topics}
