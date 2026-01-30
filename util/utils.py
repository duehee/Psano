# app/utils/common.py
from __future__ import annotations

"""
공통 유틸리티 함수 모음
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# 설정/프롬프트 캐시
# ============================================================

_config_cache: Dict[str, Any] = {}
_config_cache_time: float = 0
_prompt_cache: Dict[str, str] = {}
_prompt_cache_time: float = 0
CONFIG_CACHE_TTL = 60  # 초


# ============================================================
# ✅ 비즈니스 이벤트 로깅 유틸
# ============================================================

_event_logger = logging.getLogger("psano")


def log_event(event: str, **kwargs):
    """
    비즈니스 이벤트 로깅 (app.log)

    Usage:
        log_event("cycle_reset", cycle=2, previous=1)
        log_event("session_start", session_id=123, cycle=1)

    Output:
        [EVENT] cycle_reset | cycle=2 | previous=1
    """
    parts = [f"{k}={v}" for k, v in kwargs.items()]
    msg = f"[EVENT] {event} | " + " | ".join(parts) if parts else f"[EVENT] {event}"
    _event_logger.info(msg)


# ============================================================
# ✅ LLM RAW 로깅 유틸
# ============================================================

_llm_raw_logger = logging.getLogger("psano.llm_raw")


def _to_pretty(obj: Any) -> str:
    """
    OpenAI 응답/요청 객체를 보기 좋게 문자열로 변환.
    - pydantic model_dump() 있으면 그걸 우선
    - dict/list면 json pretty
    - 나머지는 str()
    """
    if obj is None:
        return "null"

    if hasattr(obj, "model_dump"):
        try:
            return json.dumps(obj.model_dump(), ensure_ascii=False, indent=2, default=str)
        except Exception:
            pass

    if isinstance(obj, (dict, list)):
        try:
            return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
        except Exception:
            return str(obj)

    return str(obj)


def log_llm_raw_request(tag: str, payload: Any):
    """
    LLM 요청(메시지/파라미터)을 raw로 남김.
    tag 예: "talk.start", "persona.generate" 등
    """
    _llm_raw_logger.info("[LLM][REQ][%s]\n%s", tag, _to_pretty(payload))


def log_llm_raw_response(tag: str, resp: Any, elapsed_ms: float | None = None):
    """
    LLM 응답을 raw로 남김.
    elapsed_ms가 있으면 같이 남김.
    """
    if elapsed_ms is None:
        _llm_raw_logger.info("[LLM][RESP][%s]\n%s", tag, _to_pretty(resp))
    else:
        _llm_raw_logger.info("[LLM][RESP][%s] elapsed_ms=%.1f\n%s", tag, float(elapsed_ms), _to_pretty(resp))


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


# ============================================================
# 설정 로더 (psano_config)
# ============================================================

def _load_all_configs(db: Session) -> Dict[str, Any]:
    """DB에서 모든 설정을 로드하고 타입 변환"""
    global _config_cache, _config_cache_time

    if _config_cache and (time.time() - _config_cache_time < CONFIG_CACHE_TTL):
        return _config_cache

    try:
        rows = db.execute(
            text("SELECT config_key, config_value, value_type FROM psano_config")
        ).mappings().all()
    except Exception:
        # 테이블이 없으면 빈 딕셔너리 반환
        return {}

    result = {}
    for row in rows:
        key = row.get("config_key")
        value = row.get("config_value", "")
        value_type = row.get("value_type", "str")

        if value_type == "int":
            try:
                result[key] = int(value) if value else 0
            except (ValueError, TypeError):
                result[key] = 0
        elif value_type == "float":
            try:
                result[key] = float(value) if value else 0.0
            except (ValueError, TypeError):
                result[key] = 0.0
        elif value_type == "json":
            try:
                result[key] = json.loads(value)
            except Exception:
                result[key] = value
        else:
            result[key] = value

    _config_cache = result
    _config_cache_time = time.time()
    return result


def get_config(db: Session, key: str, default: Any = None) -> Any:
    """단일 설정값 조회 (캐시 사용)"""
    configs = _load_all_configs(db)
    return configs.get(key, default)


def get_configs(db: Session, keys: list[str]) -> Dict[str, Any]:
    """여러 설정값 조회 (캐시 사용)"""
    configs = _load_all_configs(db)
    return {k: configs.get(k) for k in keys}


# ============================================================
# 프롬프트 로더 (psano_prompts)
# ============================================================

def _load_all_prompts(db: Session) -> Dict[str, str]:
    """DB에서 모든 프롬프트 템플릿 로드"""
    global _prompt_cache, _prompt_cache_time

    if _prompt_cache and (time.time() - _prompt_cache_time < CONFIG_CACHE_TTL):
        return _prompt_cache

    try:
        rows = db.execute(
            text("SELECT prompt_key, prompt_template FROM psano_prompts")
        ).mappings().all()
    except Exception:
        return {}

    result = {row.get("prompt_key"): row.get("prompt_template", "") for row in rows}

    _prompt_cache = result
    _prompt_cache_time = time.time()
    return result


def get_prompt(db: Session, key: str, default: str = "") -> str:
    """단일 프롬프트 템플릿 조회 (캐시 사용)"""
    prompts = _load_all_prompts(db)
    return prompts.get(key, default)


# ============================================================
# 캐시 초기화
# ============================================================

def clear_config_cache():
    """설정 캐시 강제 초기화"""
    global _config_cache, _config_cache_time
    _config_cache = {}
    _config_cache_time = 0


def clear_prompt_cache():
    """프롬프트 캐시 강제 초기화"""
    global _prompt_cache, _prompt_cache_time
    _prompt_cache = {}
    _prompt_cache_time = 0


def clear_all_cache():
    """모든 캐시 초기화"""
    clear_config_cache()
    clear_prompt_cache()
