import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.common import Status
from schemas.monologue import MonologueRequest, MonologueResponse

from routers.talk_policy import Action
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

    # LLM 호출 (공통 래퍼: timeout 8초, retry 2회)
    fallback_text = FALLBACK_LINES[int(time.time()) % len(FALLBACK_LINES)]
    result = call_llm(
        prompt,
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
