"""
공통 LLM 호출 래퍼
- timeout: 8초
- retry: 2회
- fallback_code 매핑
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

# 설정
LLM_TIMEOUT = 8  # 초
LLM_RETRY_COUNT = 2
DEFAULT_MODEL = "gpt-4o-mini"

client = OpenAI(timeout=LLM_TIMEOUT)


@dataclass
class LLMResult:
    """LLM 호출 결과"""
    success: bool
    content: str
    fallback_code: Optional[str] = None


def call_llm(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 150,
    fallback_text: str = "",
) -> LLMResult:
    """
    공통 LLM 호출 래퍼

    Args:
        prompt: 프롬프트 텍스트
        model: 모델명 (기본: gpt-4o-mini)
        max_tokens: 최대 토큰 수
        fallback_text: 실패 시 반환할 텍스트

    Returns:
        LLMResult: success, content, fallback_code
    """
    model = model or DEFAULT_MODEL
    last_error = None

    for attempt in range(LLM_RETRY_COUNT):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                timeout=LLM_TIMEOUT,
            )

            content = (resp.choices[0].message.content or "").strip()

            if not content:
                raise RuntimeError("empty output from LLM")

            return LLMResult(success=True, content=content, fallback_code=None)

        except Exception as e:
            last_error = e
            # 마지막 시도가 아니면 잠시 대기 후 재시도
            if attempt < LLM_RETRY_COUNT - 1:
                time.sleep(0.5)
            continue

    # 모든 재시도 실패
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