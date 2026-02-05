"""
공통 LLM 호출 래퍼
- timeout, retry, model: psano_config에서 로드 (DB 우선, fallback 하드코딩)
- fallback_code 매핑
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from openai import OpenAI

from util.utils import get_config

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# 기본값 (DB 설정 없을 때 fallback)
DEFAULT_LLM_TIMEOUT = 8
DEFAULT_LLM_RETRY_COUNT = 2
DEFAULT_LLM_MODEL = "gpt-4o"

# OpenAI 클라이언트 (timeout은 호출 시 오버라이드)
client = OpenAI(timeout=60)  # 최대 허용 timeout

_llm_raw_logger = logging.getLogger("psano.llm_raw")


@dataclass
class LLMResult:
    """LLM 호출 결과"""
    success: bool
    content: str
    fallback_code: Optional[str] = None


def call_llm(
    prompt: str,
    *,
    db: "Session | None" = None,
    model: str | None = None,
    max_tokens: int = 150,
    fallback_text: str = "",
) -> LLMResult:
    """
    공통 LLM 호출 래퍼

    Args:
        prompt: 프롬프트 텍스트
        db: DB 세션 (설정 로드용, 없으면 기본값 사용)
        model: 모델명 (기본: psano_config.default_llm_model)
        max_tokens: 최대 토큰 수
        fallback_text: 실패 시 반환할 텍스트

    Returns:
        LLMResult: success, content, fallback_code
    """
    # DB에서 설정 로드 (없으면 기본값)
    if db:
        llm_timeout = get_config(db, "llm_timeout", DEFAULT_LLM_TIMEOUT)
        llm_retry_count = get_config(db, "llm_retry_count", DEFAULT_LLM_RETRY_COUNT)
        default_model = get_config(db, "default_llm_model", DEFAULT_LLM_MODEL)
    else:
        llm_timeout = DEFAULT_LLM_TIMEOUT
        llm_retry_count = DEFAULT_LLM_RETRY_COUNT
        default_model = DEFAULT_LLM_MODEL

    model = model or default_model
    last_error = None

    for attempt in range(llm_retry_count):
        try:
            t0 = time.perf_counter()

            # GPT-5, o1, o3 모델은 max_completion_tokens 사용
            is_new_model = any(x in model for x in ['gpt-5', 'gpt-4.1', 'o1', 'o3'])

            # 요청 로그 (간결한 요약)
            prompt_len = len(prompt) if prompt else 0
            _llm_raw_logger.info(
                "[LLM][REQ] model=%s | attempt=%d/%d | max_tokens=%d | prompt_len=%d",
                model, attempt + 1, llm_retry_count, max_tokens, prompt_len
            )

            if is_new_model:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=max_tokens,
                    timeout=llm_timeout,
                )
            else:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    timeout=llm_timeout,
                )

            elapsed_ms = (time.perf_counter() - t0) * 1000

            if not resp.choices:
                _llm_raw_logger.info("[LLM][RESP] model=%s | status=error | elapsed=%.0fms | error=no_choices", model, elapsed_ms)
                raise RuntimeError("no choices in response")

            message = resp.choices[0].message
            content = (message.content or "").strip()

            if not content:
                _llm_raw_logger.info("[LLM][RESP] model=%s | status=error | elapsed=%.0fms | error=empty_content", model, elapsed_ms)
                raise RuntimeError("empty output from LLM")

            # 성공 응답 로그
            content_len = len(content)
            usage = getattr(resp, "usage", None)
            tokens_info = f"in={usage.prompt_tokens}/out={usage.completion_tokens}" if usage else "n/a"
            _llm_raw_logger.info(
                "[LLM][RESP] model=%s | status=ok | elapsed=%.0fms | tokens=%s | content_len=%d",
                model, elapsed_ms, tokens_info, content_len
            )
            # 실제 응답 내용 (별도 라인)
            _llm_raw_logger.info("[LLM][CONTENT] %s", content[:500] + "..." if len(content) > 500 else content)

            return LLMResult(success=True, content=content, fallback_code=None)

        except Exception as e:
            last_error = e
            _llm_raw_logger.info(
                "[LLM][ERROR] model=%s | attempt=%d/%d | error=%s: %s",
                model, attempt + 1, llm_retry_count, type(e).__name__, str(e)[:200]
            )
            # 마지막 시도가 아니면 잠시 대기 후 재시도
            if attempt < llm_retry_count - 1:
                time.sleep(0.5)
            continue

    # 모든 재시도 실패
    _llm_raw_logger.info("[LLM][FAILED] model=%s | all_retries_exhausted | error=%s", model, str(last_error)[:200])
    fallback_code = _map_error_to_code(last_error)
    return LLMResult(
        success=False,
        content=fallback_text,
        fallback_code=fallback_code,
    )


def _map_error_to_code(error: Exception | None) -> str:
    """에러를 fallback_code로 매핑"""
    if error is None:
        return "LLM_FAILED"

    error_str = str(error).lower()

    if "timeout" in error_str or "timed out" in error_str:
        return "LLM_TIMEOUT"

    if "rate" in error_str and "limit" in error_str:
        return "LLM_RATE_LIMIT"

    if "connection" in error_str or "network" in error_str:
        return "LLM_CONNECTION_ERROR"

    if "authentication" in error_str or "api_key" in error_str:
        return "LLM_AUTH_ERROR"

    if "empty" in error_str:
        return "LLM_EMPTY_RESPONSE"

    return "LLM_FAILED"
