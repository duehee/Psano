"""
공통 유틸리티 함수 모음
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# 시간 관련
# ============================================================

def now_kst_naive() -> datetime:
    """
    DB DATETIME에 그대로 박을 "한국 시간" (tz 없는 naive datetime)
    KST는 DST 없어서 utc+9로도 OK
    """
    return datetime.utcnow() + timedelta(hours=9)


def iso(dt) -> str | None:
    """datetime을 ISO 문자열로 변환"""
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)


# ============================================================
# 문자열 관련
# ============================================================

def trim(s: str, max_len: int) -> str:
    """문자열을 최대 길이로 자르기"""
    s = (s or "").strip()
    return s[:max_len] if len(s) > max_len else s


def summary_to_text(v: Any) -> str:
    """
    values_summary가 JSON 컬럼이면 dict로 올 수도 있고,
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


# ============================================================
# 성장단계 로드
# ============================================================

def load_growth_stage(db: Session, answered_total: int):
    """
    psano_growth_stages에서 현재 answered_total에 맞는 성장단계 로드.
    매칭되는 단계가 없으면 가장 낮은 단계 반환.
    """
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
    return db.execute(
        text("""
            SELECT stage_id, stage_name_kr, stage_name_en,
                   min_answers, max_answers, metaphor_density, certainty,
                   sentence_length, empathy_level, notes
            FROM psano_growth_stages
            ORDER BY stage_id ASC
            LIMIT 1
        """)
    ).mappings().first()