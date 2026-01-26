import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.answer import AnswerRequest, AnswerResponse
from services.llm_service import call_llm
from utils import load_growth_stage, get_config, get_prompt

router = APIRouter()

# 하드코딩 fallback (DB 없을 때)
_DEFAULT_SESSION_LIMIT = 5
_DEFAULT_FALLBACK_REACTIONS = ["흠, 그렇구나.", "알겠어.", "오케이."]
_DEFAULT_FALLBACK_LAST = "좋아. 오늘은 여기까지 해보자."

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


def _build_style_guide(db: Session, stage) -> str:
    """성장단계에 따른 스타일 가이드 생성 (임계값 DB에서 로드)"""
    if not stage:
        return ""

    metaphor = float(stage.get("metaphor_density") or 0.3)
    certainty = float(stage.get("certainty") or 0.4)
    empathy = float(stage.get("empathy_level") or 0.6)

    # 임계값 DB에서 로드
    metaphor_low = get_config(db, "style_metaphor_low", 0.25)
    metaphor_high = get_config(db, "style_metaphor_high", 0.45)
    certainty_low = get_config(db, "style_certainty_low", 0.45)
    empathy_high = get_config(db, "style_empathy_high", 0.70)

    guides = []
    if metaphor <= metaphor_low:
        guides.append("은유 없이 직접적으로")
    elif metaphor >= metaphor_high:
        guides.append("은유적으로")

    if certainty <= certainty_low:
        guides.append("조심스럽게")

    if empathy >= empathy_high:
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
    # 설정 로드
    session_limit = get_config(db, "session_question_limit", _DEFAULT_SESSION_LIMIT)
    fallback_reactions = get_config(db, "fallback_reactions", _DEFAULT_FALLBACK_REACTIONS)
    fallback_last = get_config(db, "fallback_reaction_last", _DEFAULT_FALLBACK_LAST)
    reaction_max_tokens = get_config(db, "reaction_max_tokens", 50)

    is_last = session_question_index >= session_limit

    # 성장단계 로드
    stage = load_growth_stage(db, answered_total) or {}
    stage_name = stage.get("stage_name_kr") or "태동기"
    style_guide = _build_style_guide(db, stage)
    notes = (stage.get("notes") or "").strip()

    # 프롬프트 템플릿 로드 (DB에서)
    prompt_template = get_prompt(db, "reaction_prompt", "")

    if prompt_template:
        # DB 템플릿 사용
        notes_line = f"[말투 예시: {notes}]" if notes else ""
        last_instruction = '마지막이니까 "오늘은 여기까지" 느낌으로' if is_last else "다음으로 넘어가는 느낌"

        prompt = prompt_template.format(
            stage_name=stage_name,
            style_guide=style_guide,
            notes_line=notes_line,
            question_text=question_text,
            choice=choice,
            session_question_index=session_question_index,
            session_question_limit=session_limit,
            last_instruction=last_instruction,
        )
    else:
        # fallback: 하드코딩 프롬프트
        prompt = f"""너는 전시 작품 '사노'야. 관람객이 질문에 답했어.

[성장단계: {stage_name}]
[스타일: {style_guide}]
{f'[말투 예시: {notes}]' if notes else ''}

질문: {question_text}
선택: {choice}
진행: {session_question_index}/{session_limit}

규칙:
- 한국어, 30자 이내
- 판단/평가 금지
- 가볍게 수긍하거나 호기심 표현
- {'마지막이니까 "오늘은 여기까지" 느낌으로' if is_last else '다음으로 넘어가는 느낌'}
- 위 [말투 예시]의 톤과 어미를 참고해서 말해

한 문장으로 반응해줘."""

    # fallback 텍스트 결정
    if is_last:
        fallback_text = fallback_last
    else:
        fallback_text = fallback_reactions[int(time.time()) % len(fallback_reactions)]

    # LLM 호출 (공통 래퍼: timeout 8초, retry 2회)
    result = call_llm(
        prompt,
        max_tokens=reaction_max_tokens,
        fallback_text=fallback_text,
    )

    if result.success:
        return result.content[:60]
    else:
        return result.content


@router.post("", response_model=AnswerResponse)
def post_answer(req: AnswerRequest, db: Session = Depends(get_db)):
    sid = int(req.session_id)
    qid = int(req.question_id)
    choice = req.choice

    # 설정 로드
    session_limit = get_config(db, "session_question_limit", _DEFAULT_SESSION_LIMIT)

    # 0) 세션 존재/종료 체크 + start_question_id 조회
    ses = db.execute(
        text("SELECT id, ended_at, start_question_id FROM sessions WHERE id = :sid"),
        {"sid": sid}
    ).mappings().first()

    if not ses:
        raise HTTPException(status_code=404, detail=f"session not found: {sid}")
    if ses["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="session already ended")

    start_question_id = int(ses.get("start_question_id") or 1)

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
        # 세션 내 답변 순서 검증: start_question_id + 현재답변수 == 제출 question_id
        cnt_before = db.execute(
            text("SELECT COUNT(*) AS cnt FROM answers WHERE session_id = :sid"),
            {"sid": sid}
        ).mappings().first()
        answered_before = int(cnt_before["cnt"]) if cnt_before else 0

        expected_qid = start_question_id + answered_before
        if qid != expected_qid:
            raise HTTPException(
                status_code=409,
                detail=f"question_id mismatch: expected {expected_qid}, got {qid}"
            )

        # 4) answers 저장 (psano_personality, current_question은 세션 종료 시 일괄 반영)
        db.execute(
            text("""
                INSERT INTO answers (session_id, question_id, choice, chosen_value_key)
                VALUES (:sid, :qid, :choice, :chosen_value_key)
            """),
            {"sid": sid, "qid": qid, "choice": choice, "chosen_value_key": chosen_value_key}
        )

        # 5) session_question_index 계산 (방금 저장했으니 +1)
        session_question_index = answered_before + 1
        session_should_end = (session_question_index >= session_limit)

        # 6) 전역 answered_total 계산 (GPT 반응 성장단계용)
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

    # next_question: 세션 종료 전이면 다음 질문 번호
    # (참고: psano_state.current_question은 session_service.py에서 세션 종료 시 일괄 업데이트)
    next_question = None
    if not session_should_end:
        # 다음 enabled 질문 찾기
        next_q = db.execute(
            text("""
                SELECT id
                FROM questions
                WHERE id > :qid AND enabled = 1
                ORDER BY id ASC
                LIMIT 1
            """),
            {"qid": qid}
        ).mappings().first()
        if next_q:
            next_question = int(next_q["id"])

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

    # DB에 사노 반응 저장 (실패해도 응답은 반환)
    try:
        db.execute(
            text("""
                UPDATE answers
                SET assistant_reaction = :reaction
                WHERE session_id = :sid AND question_id = :qid
            """),
            {"reaction": reaction_text, "sid": sid, "qid": qid}
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "ok": True,
        "session_should_end": session_should_end,
        "session_question_index": session_question_index,
        "chosen_value_key": chosen_value_key,
        "assistant_reaction_text": reaction_text,
        "next_question": next_question,
    }
