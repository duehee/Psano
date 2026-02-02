"""
Idle 상태 API
- 성장단계별 인사말 반환
- 혼잣말 랜덤 조회
"""
from __future__ import annotations

import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from util.utils import get_config

router = APIRouter()

# 하드코딩 fallback (DB에 데이터 없을 때)
_DEFAULT_GREETING = "어… 누구야…?\n나는 사노라고 해.\n내가 무엇인지, 어떤 존재인지도 잘 모르겠어.\n그래서… 조금 물어봐도 될까?"


def _get_default_greeting(db: Session) -> str:
    """DB에서 기본 인사말 로드 (없으면 기본값)"""
    return get_config(db, "idle_default_greeting", _DEFAULT_GREETING)

# 5개 가치축 내 대립쌍 (각 쌍에서 높은 쪽 선택)
AXIS_PAIRS = [
    ("self_direction", "conformity"),      # My way
    ("stimulation", "security"),           # Newness
    ("hedonism", "tradition"),             # This moment
    ("achievement", "benevolence"),        # growth
    ("power", "universalism"),             # together
]


# =========================
# 스키마
# =========================

class IdleRandomResponse(BaseModel):
    id: int
    axis_key: str
    text: str


# =========================
# 성장단계별 인사말
# =========================

@router.get("/greeting")
def get_idle_greeting(db: Session = Depends(get_db)):
    """
    현재 성장단계에 맞는 idle 인사말 반환.
    TouchDesigner에서 idle 상태의 사노를 클릭했을 때 호출.
    """
    # 1) 현재 사이클의 answered_total 조회
    cycle_row = db.execute(
        text("SELECT cycle_number FROM psano_state WHERE id = 1")
    ).mappings().first()
    current_cycle = int(cycle_row["cycle_number"]) if cycle_row else 1

    total_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM answers WHERE cycle_id = :cycle_id"),
        {"cycle_id": current_cycle}
    ).mappings().first()
    answered_total = int(total_row["cnt"]) if total_row else 0

    # 2) 성장단계 조회 (idle_greeting 포함)
    row = db.execute(
        text("""
            SELECT stage_id, stage_name_kr, stage_name_en, idle_greeting
            FROM psano_growth_stages
            WHERE :n BETWEEN min_answers AND max_answers
            ORDER BY stage_id ASC
            LIMIT 1
        """),
        {"n": answered_total},
    ).mappings().first()

    if not row:
        # fallback: 가장 낮은 단계
        row = db.execute(
            text("""
                SELECT stage_id, stage_name_kr, stage_name_en, idle_greeting
                FROM psano_growth_stages
                ORDER BY stage_id ASC
                LIMIT 1
            """)
        ).mappings().first()

    if not row:
        # 테이블 자체가 비어있으면 하드코딩 fallback
        return {
            "ok": True,
            "stage_id": 1,
            "stage_name_kr": "탄생",
            "stage_name_en": "birth",
            "greeting": _get_default_greeting(db),
            "answered_total": answered_total,
        }

    greeting = row.get("idle_greeting") or _get_default_greeting(db)

    return {
        "ok": True,
        "stage_id": int(row["stage_id"]),
        "stage_name_kr": row["stage_name_kr"],
        "stage_name_en": row.get("stage_name_en"),
        "greeting": greeting,
        "answered_total": answered_total,
    }


# =========================
# 랜덤 혼잣말 조회 (가치축 기반)
# =========================

def _get_preferred_values(db: Session) -> list[str]:
    """
    psano_personality에서 5개 가치축 쌍을 비교하고,
    각 쌍에서 더 높은 점수의 value를 반환 (총 5개)
    """
    row = db.execute(
        text("""
            SELECT self_direction, conformity, stimulation, security,
                   hedonism, tradition, achievement, benevolence,
                   power, universalism
            FROM psano_personality
            WHERE id = 1
        """)
    ).mappings().first()

    if not row:
        # personality 데이터 없으면 각 쌍의 첫번째 값 반환
        return [pair[0] for pair in AXIS_PAIRS]

    # 각 쌍에서 높은 쪽 선택
    preferred = []
    for val_a, val_b in AXIS_PAIRS:
        score_a = int(row.get(val_a) or 0)
        score_b = int(row.get(val_b) or 0)

        if score_a >= score_b:
            preferred.append(val_a)
        else:
            preferred.append(val_b)

    return preferred


@router.get("/random", response_model=IdleRandomResponse)
def idle_random(db: Session = Depends(get_db)):
    """
    GET /idle/random
    5개 가치축 각각에서 선호하는 value의 혼잣말 중 랜덤으로 1개 반환
    """
    try:
        # 1) 각 가치축에서 선호하는 value 조회 (5개)
        preferred_values = _get_preferred_values(db)

        # 2) 그 중 하나를 랜덤 선택
        selected_value = random.choice(preferred_values)

        # 3) 해당 value의 혼잣말 조회
        rows = db.execute(
            text("""
                SELECT id, axis_key, question_text, value
                FROM psano_idle
                WHERE enable = 1 AND value = :val
            """),
            {"val": selected_value}
        ).mappings().all()

        # 4) 해당 value에 혼잣말이 없으면 전체에서 선택
        if not rows:
            rows = db.execute(
                text("""
                    SELECT id, axis_key, question_text, value
                    FROM psano_idle
                    WHERE enable = 1
                """)
            ).mappings().all()

        if not rows:
            raise HTTPException(status_code=404, detail="No active idle monologues found")

        selected = random.choice(list(rows))

        return IdleRandomResponse(
            id=int(selected["id"]),
            axis_key=selected["axis_key"],
            text=selected["question_text"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e}")


# =========================
# 단건 조회 (by ID)
# =========================

@router.get("/monologue/{idle_id}", response_model=IdleRandomResponse)
def idle_get(idle_id: int, db: Session = Depends(get_db)):
    """
    GET /idle/monologue/{idle_id}
    특정 ID의 혼잣말 조회
    """
    try:
        row = db.execute(
            text("""
                SELECT id, axis_key, question_text
                FROM psano_idle
                WHERE id = :id AND enable = 1
            """),
            {"id": idle_id}
        ).mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail=f"Idle monologue not found: {idle_id}")

        return IdleRandomResponse(
            id=int(row["id"]),
            axis_key=row["axis_key"],
            text=row["question_text"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db error: {e}")
