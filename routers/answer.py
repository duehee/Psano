from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from openai import OpenAI

from database import get_db
from schemas.answer import AnswerRequest, AnswerResponse

router = APIRouter()
client = OpenAI()

SESSION_QUESTION_LIMIT = 5
MAX_QUESTIONS = 380

ALLOWED_VALUE_KEYS = {
    "self_direction",
    "conformity",
    "stimulation",
    "security",
    "hedonism",
    "tradition",
    "achievement",
    "benevolence",
    "power",
    "universalism",
}

FALLBACK_REACTIONS = [
    "흠, 그렇구나.",
    "알겠어.",
    "오케이.",
]


def _load_growth_stage(db: Session, answered_total: int):
    """monolouge.py와 동일한 성장단계 로드"""
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

    # fallback: 가장 낮은 단계
    row2 = db.execute(
        text("""
            SELECT stage_id, stage_name_kr, stage_name_en,
                   min_answers, max_answers, metaphor_density, certainty,
                   sentence_length, empathy_level, notes
            FROM psano_growth_stages
            ORDER BY stage_id ASC
            LIMIT 1
        """)
    ).mappings().first()

    return row2


def _build_style_guide(stage) -> str:
    """성장단계에 따른 스타일 가이드 생성"""
    if not stage:
        return ""

    metaphor = float(stage.get("metaphor_density") or 0.3)
    certainty = float(stage.get("certainty") or 0.4)
    empathy = float(stage.get("empathy_level") or 0.6)

    guides = []
    if metaphor <= 0.25:
        guides.append("은유 없이 직접적으로")
    elif metaphor >= 0.45:
        guides.append("은유적으로")

    if certainty <= 0.45:
        guides.append("조심스럽게")

    if empathy >= 0.7:
        guides.append("공감하며")

    return ", ".join(guides) if guides else "담백하게"


def _reaction_text_gpt(
    db: Session,
    question_text: str,
    choice: str,
    chosen_value_key: str,
    session_question_index: int,
    answered_total: int,
) -> str:
    """유저 답변에 GPT가 성장단계 스타일로 짧게 반응"""
    import time

    is_last = session_question_index >= SESSION_QUESTION_LIMIT

    # 성장단계 로드
    stage = _load_growth_stage(db, answered_total)
    stage_name = stage.get("stage_name_kr") if stage else "태동기"
    style_guide = _build_style_guide(stage)

    prompt = f"""너는 전시 작품 '사노'야. 관람객이 질문에 답했어.

[성장단계: {stage_name}]
[스타일: {style_guide}]

질문: {question_text}
선택: {choice}
진행: {session_question_index}/{SESSION_QUESTION_LIMIT}

규칙:
- 한국어, 30자 이내
- 판단/평가 금지
- 가볍게 수긍하거나 호기심 표현
- {'마지막이니까 "오늘은 여기까지" 느낌으로' if is_last else '다음으로 넘어가는 느낌'}

한 문장으로 반응해줘."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text[:60] if text else FALLBACK_REACTIONS[int(time.time()) % len(FALLBACK_REACTIONS)]
    except Exception:
        # fallback
        if is_last:
            return "좋아. 오늘은 여기까지 해보자."
        return FALLBACK_REACTIONS[int(time.time()) % len(FALLBACK_REACTIONS)]

@router.post("", response_model=AnswerResponse)
def post_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    qid = int(req.question_id)
    choice = req.choice

    # 0) 세션 존재/종료 체크
    ses = db.execute(
        text("SELECT id, ended_at FROM sessions WHERE id = :sid"),
        {"sid": sid}
    ).mappings().first()

    if not ses:
        raise HTTPException(status_code=404, detail=f"session not found: {sid}")
    if ses["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    # 중복 제출 방지: 같은 session_id + question_id 이미 있으면 409
    dup = db.execute(
        text("""
            SELECT id
            FROM answers
            WHERE session_id = :sid AND question_id = :qid
            LIMIT 1
        """),
        {"sid": sid, "qid": qid}
    ).mappings().first()

    if dup:
        raise HTTPException(status_code=409, detail="already answered")

    # 1) 질문 조회(가치키 포함, GPT 반응용 question_text도)
    q = db.execute(
        text("""
            SELECT id, enabled, value_a_key, value_b_key, question_text
            FROM questions
            WHERE id = :qid
        """),
        {"qid": qid}
    ).mappings().first()

    if not q:
        raise HTTPException(status_code=404, detail=f"question not found: {qid}")
    if not bool(q["enabled"]):
        raise HTTPException(status_code=409, detail=f"question disabled: {qid}")

    value_a_key = q.get("value_a_key")
    value_b_key = q.get("value_b_key")

    # 2) chosen_value_key 결정
    if choice == "A":
        chosen_value_key = (value_a_key or "").strip()
    else:
        chosen_value_key = (value_b_key or "").strip()

    if not chosen_value_key:
        raise HTTPException(status_code=400, detail="chosen_value_key is empty (check value_a_key/value_b_key)")

    # 3) value key whitelist 검증
    if chosen_value_key not in ALLOWED_VALUE_KEYS:
        raise HTTPException(status_code=400, detail=f"invalid chosen_value_key: {chosen_value_key}")

    try:
        # current_question 일치 검증 (전역 번호 꼬임 방지)
        st = db.execute(
            text("""
                SELECT current_question
                FROM psano_state
                WHERE id = 1
            """)
        ).mappings().first()

        if not st:
            raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

        current_q = int(st["current_question"])
        if current_q != qid:
            raise HTTPException(status_code=409, detail="question_id mismatch with current_question")

        # 4) answers 저장
        db.execute(
            text("""
                INSERT INTO answers (session_id, question_id, choice, chosen_value_key)
                VALUES (:sid, :qid, :choice, :chosen_value_key)
            """),
            {"sid": sid, "qid": qid, "choice": choice, "chosen_value_key": chosen_value_key}
        )

        # 5) psano_personality +1
        col = chosen_value_key
        db.execute(
            text(f"UPDATE psano_personality SET `{col}` = `{col}` + 1 WHERE id = 1")
        )

        # 6) session_question_index 계산(방금 저장했으니 COUNT가 곧 index)
        cnt_row = db.execute(
            text("SELECT COUNT(*) AS cnt FROM answers WHERE session_id = :sid"),
            {"sid": sid}
        ).mappings().first()
        answered_cnt = int(cnt_row["cnt"]) if cnt_row else 0
        session_question_index = answered_cnt
        session_should_end = (session_question_index >= SESSION_QUESTION_LIMIT)

        # 다음 질문을 current+1이 아니라 "다음 enabled"로 세팅 (안정)
        next_q = db.execute(
            text("""
                SELECT id
                FROM questions
                WHERE id > :qid AND enabled = 1
                ORDER BY id ASC
                LIMIT 1
            """),
            {"qid": current_q}
        ).mappings().first()

        if next_q:
            new_current_q = int(next_q["id"])
        else:
            # 더 없으면 formation 완료로 처리되게 MAX+1로 보내기
            new_current_q = MAX_QUESTIONS + 1

        db.execute(
            text("""
                UPDATE psano_state
                SET current_question = :new_q
                WHERE id = 1
            """),
            {"new_q": new_current_q}
        )

        # 7) 전역 answered_total 계산 (GPT 반응 성장단계용)
        total_row = db.execute(
            text("SELECT COUNT(*) AS cnt FROM answers")
        ).mappings().first()
        answered_total = int(total_row["cnt"]) if total_row else 0

        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    # next_question은 세션 종료면 None, 아니면 다음 current_question(단, formation 끝났으면 None)
    next_question = None
    if not session_should_end and new_current_q <= MAX_QUESTIONS:
        next_question = new_current_q

    # GPT 반응 생성 (성장단계 스타일 반영)
    question_text = q.get("question_text") or ""
    reaction_text = _reaction_text_gpt(
        db,
        question_text,
        choice,
        chosen_value_key,
        session_question_index,
        answered_total,
    )

    return {
        "ok": True,
        "session_should_end": session_should_end,
        "session_question_index": session_question_index,
        "chosen_value_key": chosen_value_key,
        "assistant_reaction_text": reaction_text,
        "next_question": next_question,
    }
