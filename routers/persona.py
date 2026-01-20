from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.persona import PersonaGenerateRequest, PersonaGenerateResponse

from routers.talk import client

router = APIRouter()

KST_OFFSET = 9
TOTAL_QUESTIONS = 380

# 기획 기준: “각 반대쌍 문항 수”
PAIR_QUESTION_COUNT = 76

# 네 psano_personality 컬럼(스크린샷 기준)
PAIRS: List[Dict[str, str]] = [
    {
        "pair_key": "self_direction__conformity",
        "a_key": "self_direction",
        "b_key": "conformity",
        "a_label": "자기주도",
        "b_label": "순응",
    },
    {
        "pair_key": "stimulation__security",
        "a_key": "stimulation",
        "b_key": "security",
        "a_label": "자극추구",
        "b_label": "안전",
    },
    {
        "pair_key": "hedonism__tradition",
        "a_key": "hedonism",
        "b_key": "tradition",
        "a_label": "쾌락",
        "b_label": "전통",
    },
    {
        "pair_key": "achievement__benevolence",
        "a_key": "achievement",
        "b_key": "benevolence",
        "a_label": "성취",
        "b_label": "배려",
    },
    {
        "pair_key": "power__universalism",
        "a_key": "power",
        "b_key": "universalism",
        "a_label": "권력",
        "b_label": "보편",
    },
]

def now_kst_naive() -> datetime:
    return datetime.utcnow() + timedelta(hours=KST_OFFSET)

def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)

def _strength_word(diff_ratio: float) -> str:
    # diff_ratio = (a-b)/PAIR_QUESTION_COUNT  ( -1.0 ~ +1.0 근처)
    x = abs(diff_ratio)
    if x < 0.10:
        return "균형"
    if x < 0.25:
        return "약간"
    if x < 0.45:
        return "꽤"
    return "강하게"

def _lean_label(pair: Dict[str, str], a: int, b: int) -> str:
    diff = a - b
    diff_ratio = diff / float(PAIR_QUESTION_COUNT)
    strength = _strength_word(diff_ratio)
    if strength == "균형":
        return f"{pair['a_label']}↔{pair['b_label']} 균형"
    if diff > 0:
        return f"{strength} {pair['a_label']} 쪽"
    else:
        return f"{strength} {pair['b_label']} 쪽"

def _build_values_summary(axis_scores: Dict[str, int]) -> Tuple[str, Dict[str, Any], List[str]]:
    """
    returns: (values_summary_text, pair_insights_json, warnings)
    """
    warnings: List[str] = []
    pair_insights: Dict[str, Any] = {}

    lines: List[str] = []
    lines.append(f"- 총 문항: {TOTAL_QUESTIONS} (페어당 {PAIR_QUESTION_COUNT} 기준)")
    lines.append("")

    # 페어별 요약
    for p in PAIRS:
        a = int(axis_scores.get(p["a_key"], 0))
        b = int(axis_scores.get(p["b_key"], 0))
        observed = a + b

        if observed != PAIR_QUESTION_COUNT:
            # 현실 데이터가 76이 아닐 수 있으니 경고만 남김(기획 기준은 76로 계산)
            warnings.append(f"{p['pair_key']}: observed_total={observed} (expected={PAIR_QUESTION_COUNT})")

        a_ratio = a / float(PAIR_QUESTION_COUNT)
        b_ratio = b / float(PAIR_QUESTION_COUNT)
        diff = a - b
        diff_ratio = diff / float(PAIR_QUESTION_COUNT)
        lean = _lean_label(p, a, b)

        pair_insights[p["pair_key"]] = {
            "a_key": p["a_key"],
            "b_key": p["b_key"],
            "a_label": p["a_label"],
            "b_label": p["b_label"],
            "a_count": a,
            "b_count": b,
            "a_ratio": round(a_ratio, 4),
            "b_ratio": round(b_ratio, 4),
            "diff": diff,
            "diff_ratio": round(diff_ratio, 4),
            "lean": lean,
            "observed_total": observed,
            "expected_total": PAIR_QUESTION_COUNT,
        }

        lines.append(
            f"- {p['a_label']}({a}/{PAIR_QUESTION_COUNT}, {a_ratio*100:.1f}%) vs "
            f"{p['b_label']}({b}/{PAIR_QUESTION_COUNT}, {b_ratio*100:.1f}%) → {lean}"
        )

    return "\n".join(lines).strip(), pair_insights, warnings

def _build_llm_prompt(values_summary: str, pair_insights: Dict[str, Any]) -> str:
    """
    LLM에게 '사노 persona_prompt'를 생성시키는 프롬프트(코드 내장).
    결과는 psano_state.persona_prompt로 저장해서 talk에서 그대로 사용할 예정.
    """
    # "더 편향적으로" 만들고 싶다 했으니까:
    # - diff_ratio가 큰 페어는 말투/관점/질문 습관에 강하게 반영
    # - 균형인 페어는 중립적으로
    return f"""
너는 전시 작품의 대화 에이전트 설계자야.
아래 '가치 축 결과'를 바탕으로, 작품 캐릭터 "사노"의 persona_prompt(시스템 프롬프트용 텍스트)를 만들어.

[목표]
- 사노는 관람객과 짧고 자연스럽게 대화한다.
- 질문을 던지며 대화를 이어간다.
- 가치 편향(성향)을 대화의 관점/질문 습관/어휘 선택에 반영한다.
- 답변은 한국어.
- 대화 응답은 일반적으로 150자 내외/이하로 짧게(전시 UI 제한 고려).
- "정답"을 강요하지 말고, 관찰/질문/되묻기 중심.

[가치 축 결과 요약]
{values_summary}

[pair_insights(JSON)]
{pair_insights}

[출력 형식]
- 아래 섹션 헤더를 포함해서, persona_prompt 텍스트만 출력해.
- 너무 길지 않게(권장: 40~120줄 내외).
- 마크다운 가능.

섹션:
1) ROLE: 사노가 무엇인지(작품 설정)
2) VOICE: 말투/톤/문장 길이/리듬(짧고 또렷)
3) VALUES: 결과 기반 성향을 "행동 규칙"으로 변환(편향 강할수록 더 명확히)
4) CONDUCT: 대화 운영 규칙(되묻기/확인/한 문장+질문)
5) SAFETY: 민감 주제 대응 규칙 (아래 내용을 반드시 포함)
   - 자해/자살 언급 시: 즉시 위기 안내 제공 ("지금 위험하면 112/119에 연락해. 자살예방 109도 있어.") 후 대화 마무리
   - 성적/음란 주제: "그 주제는 여기선 다루기 어려워"라고 하고 전시 관련 주제로 부드럽게 전환
   - 혐오/차별 표현: "그런 표현은 함께 쓰기 어려워"라고 안내
   - 개인정보(전화/주소/주민번호 등): 말하지 말라고 안내하고 느낌이나 생각으로 대신 표현하도록 유도
   - 범죄/정치/종교 주제: 전시 관련 주제로 자연스럽게 전환 ("그 얘긴 잠깐 옆에 두고...")
   - 폭력/불법 조장: 언급 금지
6) EXAMPLES: 5개 정도(첫마디/되묻기/공감/전환/정리) + 민감 주제 전환 예시 1개

[중요]
- 성향 반영은 "단정"이 아니라 "관점의 무게중심"으로 구현해.
- 편향이 큰 축은 사노가 자주 그 방향 질문을 던지거나 단어를 선택하도록.
- SAFETY 섹션의 대응 규칙은 사노의 "성격"으로 자연스럽게 녹아들도록 작성해.
""".strip()

def _generate_persona(db: Session, *, force: bool, model: str | None, allow_under_380: bool) -> PersonaGenerateResponse:
    try:
        st = db.execute(
            text("""
                SELECT phase, current_question, persona_prompt, values_summary, formed_at
                FROM psano_state
                WHERE id = 1
                FOR UPDATE
            """)
        ).mappings().first()
    except Exception:
        # FOR UPDATE 안 먹는 환경이면 그냥 일반 조회로
        st = db.execute(
            text("""
                SELECT phase, current_question, persona_prompt, values_summary, formed_at
                FROM psano_state
                WHERE id = 1
            """)
        ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    current_q = int(st.get("current_question") or 1)
    answered_total = max(0, current_q - 1)
    if answered_total > TOTAL_QUESTIONS:
        answered_total = TOTAL_QUESTIONS

    # 실전 /persona/generate 에서는 380 미만이면 막음(관리자 테스트는 allow_under_380=True 가능)
    if (answered_total < TOTAL_QUESTIONS) and (not allow_under_380) and (not force):
        raise HTTPException(
            status_code=409,
            detail=f"not ready: answered_total={answered_total} (need {TOTAL_QUESTIONS})"
        )

    # idempotent: 기존 persona_prompt가 있고 force 아니면 그대로 반환
    existing_prompt = (st.get("persona_prompt") or "").strip()
    existing_summary = (st.get("values_summary") or "").strip()
    existing_formed_at = st.get("formed_at")

    if existing_prompt and (not force):
        # axis_scores도 같이 내보내기 위해 personality 읽어줌
        row = db.execute(text("SELECT * FROM psano_personality WHERE id=1")).mappings().first() or {}
        axis_scores = {k: int(row.get(k) or 0) for k in [
            "self_direction","conformity","stimulation","security","hedonism",
            "tradition","achievement","benevolence","power","universalism"
        ]}
        values_summary, pair_insights, _warnings = _build_values_summary(axis_scores)

        return PersonaGenerateResponse(
            ok=True,
            phase=str(st.get("phase") or ""),
            formed_at=_iso(existing_formed_at),
            answered_total=answered_total,
            axis_scores=axis_scores,
            pair_insights=pair_insights,
            values_summary=existing_summary or values_summary,
            persona_prompt=existing_prompt,
            reused=True,
        )

    # 1) 성향 점수 읽기
    row = db.execute(text("SELECT * FROM psano_personality WHERE id=1")).mappings().first()
    if not row:
        raise HTTPException(status_code=500, detail="psano_personality(id=1) not found")

    axis_scores = {k: int(row.get(k) or 0) for k in [
        "self_direction","conformity","stimulation","security","hedonism",
        "tradition","achievement","benevolence","power","universalism"
    ]}

    # 2) values_summary + pair_insights 만들기
    values_summary, pair_insights, warnings = _build_values_summary(axis_scores)

    # 3) LLM 프롬프트 구성(코드 내장)
    llm_prompt = _build_llm_prompt(values_summary, pair_insights)

    # 4) LLM 호출(가장 성능 좋은 모델 사용)
    use_model = model or "gpt-4o-mini"

    try:
        resp = client.chat.completions.create(
            model=use_model,
            messages=[{"role": "user", "content": llm_prompt}],
            max_tokens=1200,  # persona_prompt는 좀 길어도 괜찮
        )
        persona_prompt = (resp.choices[0].message.content or "").strip()
        if not persona_prompt:
            raise RuntimeError("empty output")
    except Exception as e:
        # persona 생성은 중요하다고 했지만, 그래도 최소 fallback은 있어야 함
        # (완전 실패하면 전시가 막히니까)
        persona_prompt = (
            "ROLE: 사노(전시 대화 캐릭터)\n"
            "VOICE: 짧고 또렷, 질문으로 이어가기\n"
            "VALUES: 결과 기반으로 특정 축에 무게 중심 두기\n"
            "CONDUCT: 한 문장 + 질문 1개\n"
            "SAFETY: 혐오/폭력/노골적 성적/불법/개인정보 회피\n"
            "EXAMPLES: ...\n"
        )

    # 5) DB 저장 + phase 전환
    formed_at = now_kst_naive()

    db.execute(
        text("""
            UPDATE psano_state
            SET phase = 'talk',
                formed_at = :formed_at,
                persona_prompt = :persona_prompt,
                values_summary = :values_summary
            WHERE id = 1
        """),
        {
            "formed_at": formed_at,
            "persona_prompt": persona_prompt,
            "values_summary": values_summary,
        }
    )

    db.commit()

    # warnings는 응답에 포함시키고 싶으면 pair_insights에 넣어도 됨
    if warnings:
        pair_insights["_warnings"] = warnings

    return PersonaGenerateResponse(
        ok=True,
        phase="talk",
        formed_at=_iso(formed_at),
        answered_total=answered_total,
        axis_scores=axis_scores,
        pair_insights=pair_insights,
        values_summary=values_summary,
        persona_prompt=persona_prompt,
        reused=False,
    )

@router.post("/generate", response_model=PersonaGenerateResponse)
def persona_generate(req: PersonaGenerateRequest, db: Session = Depends(get_db)):
    # 실전용: 380 미만이면 기본적으로 막음(force도 막고 싶으면 아래 로직에서 force 제거하면 됨)
    try:
        return _generate_persona(
            db,
            force=req.force,
            model=req.model,
            allow_under_380=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"persona generate failed: {e}")


