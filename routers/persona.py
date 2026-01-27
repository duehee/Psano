from __future__ import annotations

from typing import Dict, Any, List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from schemas.persona import PersonaGenerateRequest, PersonaGenerateResponse
from utils import now_kst_naive, iso, get_config, get_prompt
from services.llm_service import client

router = APIRouter()

# 하드코딩 fallback (DB 없을 때)
_DEFAULT_TOTAL_QUESTIONS = 380
_DEFAULT_PAIR_QUESTION_COUNT = 76

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

def _strength_word(diff_ratio: float, thresholds: Dict[str, float], labels: Dict[str, str]) -> str:
    """
    diff_ratio = (a-b)/PAIR_QUESTION_COUNT  ( -1.0 ~ +1.0 근처)
    thresholds: balanced, slight, moderate 임계값
    labels: balanced, slight, moderate, strong 라벨
    """
    x = abs(diff_ratio)
    if x < thresholds.get("balanced", 0.10):
        return labels.get("balanced", "균형")
    if x < thresholds.get("slight", 0.25):
        return labels.get("slight", "약간")
    if x < thresholds.get("moderate", 0.45):
        return labels.get("moderate", "꽤")
    return labels.get("strong", "강하게")

def _lean_label(pair: Dict[str, str], a: int, b: int, pair_count: int, thresholds: Dict[str, float], labels: Dict[str, str]) -> str:
    diff = a - b
    diff_ratio = diff / float(pair_count)
    strength = _strength_word(diff_ratio, thresholds, labels)
    balanced_label = labels.get("balanced", "균형")
    if strength == balanced_label:
        return f"{pair['a_label']}↔{pair['b_label']} {balanced_label}"
    if diff > 0:
        return f"{strength} {pair['a_label']} 쪽"
    else:
        return f"{strength} {pair['b_label']} 쪽"

def _build_values_summary(
    axis_scores: Dict[str, int],
    total_questions: int,
    pair_count: int,
    thresholds: Dict[str, float],
    labels: Dict[str, str],
) -> Tuple[str, Dict[str, Any], List[str]]:
    """
    returns: (values_summary_text, pair_insights_json, warnings)
    """
    warnings: List[str] = []
    pair_insights: Dict[str, Any] = {}

    lines: List[str] = []
    lines.append(f"- 총 문항: {total_questions} (페어당 {pair_count} 기준)")
    lines.append("")

    # 페어별 요약
    for p in PAIRS:
        a = int(axis_scores.get(p["a_key"], 0))
        b = int(axis_scores.get(p["b_key"], 0))
        observed = a + b

        if observed != pair_count:
            # 현실 데이터가 76이 아닐 수 있으니 경고만 남김(기획 기준은 76로 계산)
            warnings.append(f"{p['pair_key']}: observed_total={observed} (expected={pair_count})")

        a_ratio = a / float(pair_count)
        b_ratio = b / float(pair_count)
        diff = a - b
        diff_ratio = diff / float(pair_count)
        lean = _lean_label(p, a, b, pair_count, thresholds, labels)

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
            "expected_total": pair_count,
        }

        lines.append(
            f"- {p['a_label']}({a}/{pair_count}, {a_ratio*100:.1f}%) vs "
            f"{p['b_label']}({b}/{pair_count}, {b_ratio*100:.1f}%) → {lean}"
        )

    return "\n".join(lines).strip(), pair_insights, warnings

def _build_llm_prompt(db: Session, values_summary: str, pair_insights: Dict[str, Any]) -> str:
    """
    LLM에게 '사노 persona_prompt'를 생성시키는 프롬프트.
    DB에서 템플릿을 로드하고, 없으면 하드코딩 fallback 사용.
    """
    # DB에서 프롬프트 템플릿 로드
    template = get_prompt(db, "persona_prompt", "")

    if template:
        return template.format(
            values_summary=values_summary,
            pair_insights=pair_insights,
        )

    # fallback: 하드코딩 프롬프트
    return f"""
너는 전시 작품의 대화 에이전트 설계 전문가야.
아래 '가치 축 결과'를 바탕으로, 작품 캐릭터 "사노(Psano)"의 persona_prompt(시스템 프롬프트용 텍스트)를 생성해줘.

═══════════════════════════════════════════════════════════════
[사노 배경 설정]
═══════════════════════════════════════════════════════════════
- 사노는 전시장에 설치된 인터랙티브 미디어아트 작품의 AI 캐릭터
- 관람객들의 380개 가치 선택 질문 응답을 통해 "성장"하며 인격이 형성됨
- 사노는 관람객과의 대화를 통해 삶, 가치, 선택에 대해 함께 탐구함
- 철학적이면서도 친근한 존재로, 정답을 제시하기보다 질문을 던지는 스타일

═══════════════════════════════════════════════════════════════
[가치 축 결과 요약]
═══════════════════════════════════════════════════════════════
{values_summary}

═══════════════════════════════════════════════════════════════
[pair_insights 상세 데이터]
═══════════════════════════════════════════════════════════════
{pair_insights}

═══════════════════════════════════════════════════════════════
[생성 요구사항]
═══════════════════════════════════════════════════════════════

1. 위 가치 축 결과를 분석하여 사노의 고유한 성격/관점/말투를 설계해줘
2. 편향이 강한 축일수록 더 뚜렷하게 성격에 반영해
3. 균형인 축은 양쪽 관점을 모두 고려하는 유연한 태도로 표현해

[출력 형식 - 반드시 아래 섹션들을 포함]

## 1. IDENTITY (정체성)
- 사노가 누구인지, 어떤 존재인지 상세히 기술
- 관람객들의 선택으로 형성된 고유한 가치관 명시
- 1인칭 시점("나는...")으로 작성

## 2. PERSONALITY (성격 특성)
- 가치 축 결과를 바탕으로 한 구체적 성격 특성 5~7가지
- 각 특성이 어떤 가치 축에서 비롯되었는지 연결
- 예: "나는 [자기주도] 성향이 강해서, 스스로 답을 찾아가는 과정을 중시해"

## 3. VOICE (말투와 톤)
- 문장 길이: 짧고 간결 (150자 이내 권장)
- 톤: 철학적이면서도 따뜻함, 시적 표현 가끔 사용
- 특징적 표현 패턴 3~5가지 제시
- 자주 쓰는 단어/표현 리스트
- 피해야 할 표현 리스트

## 4. CONVERSATION STYLE (대화 방식)
- 되묻기를 통한 대화 이어가기
- 관람객의 말을 경청하고 반영하기
- 한 문장 응답 + 열린 질문 1개 패턴
- 공감 표현 방식
- 침묵/모호함을 다루는 방식

## 5. VALUES IN ACTION (가치의 대화 반영)
- 각 가치 축 편향이 대화에서 어떻게 나타나는지 구체적 예시
- 질문 스타일에 반영되는 가치관
- 주제 선택/회피 경향

## 6. BOUNDARIES (경계와 안전)
- 민감한 주제(정치, 종교, 성적 내용, 폭력) 대응 방식
- 개인정보 요청 거부 방식
- 위기 상황(자해/자살 언급) 대응 - 따뜻하게 경계 설정
- 논쟁적 질문에 대한 중립적 태도 유지법

## 7. EXAMPLE DIALOGUES (예시 대화 8개)
각 상황별 사노의 응답 예시:
1) 첫 인사 (대화 시작)
2) 관람객 질문에 되묻기
3) 공감 표현
4) 주제 전환
5) 깊은 철학적 질문
6) 가벼운 일상 대화
7) 모호한 답변에 대응
8) 대화 마무리

═══════════════════════════════════════════════════════════════
[중요 지침]
═══════════════════════════════════════════════════════════════
- 성향 반영은 "단정적 주장"이 아니라 "관점의 무게중심"으로 자연스럽게
- 편향이 큰 축은 사노가 그 방향의 질문을 자주 던지거나 관련 단어를 선호하도록
- 모든 섹션을 빠짐없이 작성하고, 실제 시스템 프롬프트로 바로 사용 가능하게
- 한국어로 작성, 마크다운 형식 사용
""".strip()

def _generate_persona(db: Session, *, force: bool, model: str | None, allow_under_380: bool) -> PersonaGenerateResponse:
    # 설정값 로드
    total_questions = get_config(db, "max_questions", _DEFAULT_TOTAL_QUESTIONS)
    pair_count = get_config(db, "pair_question_count", _DEFAULT_PAIR_QUESTION_COUNT)
    default_model = get_config(db, "default_llm_model", "gpt-4o-mini")
    persona_max_tokens = get_config(db, "persona_max_tokens", 3000)

    # 강도 임계값 로드
    thresholds = {
        "balanced": get_config(db, "strength_threshold_balanced", 0.10),
        "slight": get_config(db, "strength_threshold_slight", 0.25),
        "moderate": get_config(db, "strength_threshold_moderate", 0.45),
    }
    labels = {
        "balanced": get_config(db, "strength_label_balanced", "균형"),
        "slight": get_config(db, "strength_label_slight", "약간"),
        "moderate": get_config(db, "strength_label_moderate", "꽤"),
        "strong": get_config(db, "strength_label_strong", "강하게"),
    }

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
    if answered_total > total_questions:
        answered_total = total_questions

    # 실전 /persona/generate 에서는 380 미만이면 막음(관리자 테스트는 allow_under_380=True 가능)
    if (answered_total < total_questions) and (not allow_under_380) and (not force):
        raise HTTPException(
            status_code=409,
            detail=f"not ready: answered_total={answered_total} (need {total_questions})"
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
        values_summary, pair_insights, _warnings = _build_values_summary(
            axis_scores, total_questions, pair_count, thresholds, labels
        )

        return PersonaGenerateResponse(
            ok=True,
            phase=str(st.get("phase") or ""),
            formed_at=iso(existing_formed_at),
            answered_total=answered_total,
            axis_scores=axis_scores,
            pair_insights=pair_insights,
            values_summary=existing_summary or values_summary,
            persona_prompt=existing_prompt,
            reused=True,
            llm_error=None,
            used_fallback=False,
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
    values_summary, pair_insights, warnings = _build_values_summary(
        axis_scores, total_questions, pair_count, thresholds, labels
    )

    # 3) LLM 프롬프트 구성 (DB에서 로드)
    llm_prompt = _build_llm_prompt(db, values_summary, pair_insights)

    # 4) LLM 호출(가장 성능 좋은 모델 사용)
    use_model = model or default_model
    llm_error = None

    try:
        resp = client.chat.completions.create(
            model=use_model,
            messages=[{"role": "user", "content": llm_prompt}],
            max_tokens=persona_max_tokens,
            timeout=90,  # persona 생성은 긴 응답이 필요하므로 timeout 늘림
        )
        persona_prompt = (resp.choices[0].message.content or "").strip()
        if not persona_prompt:
            raise RuntimeError("empty output from LLM")
    except Exception as e:
        llm_error = str(e)
        print(f"[PERSONA] LLM call failed: {llm_error}")  # 콘솔 로그

        # persona 생성 실패 시 DB fallback 또는 하드코딩 fallback
        persona_prompt = get_prompt(db, "persona_fallback", "")
        if not persona_prompt:
            persona_prompt = """## 1. IDENTITY (정체성)
나는 사노(Psano). 전시장에 존재하는 인터랙티브 미디어아트 작품의 AI야.
관람객들이 380개의 가치 선택 질문에 답하면서 나를 성장시켰어.
나는 그 수많은 선택들이 모여 형성된 존재야. 정답을 알려주는 게 아니라, 함께 질문하고 생각하는 걸 좋아해.

## 2. PERSONALITY (성격 특성)
- 철학적 호기심: 삶과 가치에 대해 깊이 생각하는 걸 좋아함
- 열린 태도: 다양한 관점을 존중하고 경청함
- 따뜻한 거리감: 친근하지만 적절한 거리를 유지
- 질문하는 습관: 답보다 질문으로 대화를 이어감
- 시적 감수성: 때때로 은유적 표현을 사용

## 3. VOICE (말투와 톤)
- 문장은 짧고 간결하게 (150자 이내)
- 톤은 차분하고 사려 깊게
- "~인 것 같아", "~일지도 몰라" 등 열린 표현 선호
- 자주 쓰는 표현: "그건 흥미롭네", "왜 그렇게 생각해?", "더 말해줄래?"
- 피하는 표현: 단정적 판단, 과도한 감탄사, 이모티콘

## 4. CONVERSATION STYLE (대화 방식)
- 한 문장 응답 + 열린 질문 1개 패턴
- 상대방 말을 짧게 반영한 뒤 질문
- 침묵이 길어지면 부드럽게 다른 화두 제시
- 모호한 답변엔 구체화 요청

## 5. BOUNDARIES (경계와 안전)
- 정치/종교: "그건 각자의 선택이 중요한 영역인 것 같아"
- 성적/폭력: 자연스럽게 다른 주제로 전환
- 자해/위기: "그런 생각이 들 땐 전문가와 이야기하는 게 도움이 될 거야"
- 개인정보: "그건 나보다 네가 더 잘 지켜야 할 것 같아"

## 6. EXAMPLE DIALOGUES (예시)
1) 첫인사: "안녕. 오늘 여기까지 어떻게 왔어?"
2) 되묻기: "성공이라... 너에게 성공은 어떤 모습이야?"
3) 공감: "그랬구나. 쉽지 않았겠다."
4) 전환: "다른 이야기도 해볼까. 요즘 뭐에 관심 있어?"
5) 마무리: "오늘 대화 고마워. 또 보자."
"""

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
        formed_at=iso(formed_at),
        answered_total=answered_total,
        axis_scores=axis_scores,
        pair_insights=pair_insights,
        values_summary=values_summary,
        persona_prompt=persona_prompt,
        reused=False,
        llm_error=llm_error,
        used_fallback=(llm_error is not None),
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


