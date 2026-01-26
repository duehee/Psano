"""
Idle 상태에서 클릭 시 성장단계별 인사말 반환 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from utils import load_growth_stage

router = APIRouter()

# 하드코딩 fallback (DB에 데이터 없을 때)
_DEFAULT_GREETING = "어… 누구야…?\n나는 사노라고 해.\n내가 무엇인지, 어떤 존재인지도 잘 모르겠어.\n그래서… 조금 물어봐도 될까?"


@router.get("/greeting")
def get_idle_greeting(db: Session = Depends(get_db)):
    """
    현재 성장단계에 맞는 idle 인사말 반환.
    TouchDesigner에서 idle 상태의 사노를 클릭했을 때 호출.
    """
    # 1) 현재 answered_total 조회
    total_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM answers")
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
            "greeting": _DEFAULT_GREETING,
            "answered_total": answered_total,
        }

    greeting = row.get("idle_greeting") or _DEFAULT_GREETING

    return {
        "ok": True,
        "stage_id": int(row["stage_id"]),
        "stage_name_kr": row["stage_name_kr"],
        "stage_name_en": row.get("stage_name_en"),
        "greeting": greeting,
        "answered_total": answered_total,
    }
