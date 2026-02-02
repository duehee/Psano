
import time
import logging
import traceback
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

access_logger = logging.getLogger("psano.access")
app_logger = logging.getLogger("psano")

MASK_QUERY_KEYS = {"template"}  # 여기에 마스킹할 키 추가
MASK_BODY_KEYS = {"password", "token", "secret"}  # body에서 마스킹할 키


def _masked_query(request: Request) -> str:
    items = []
    for k, v in request.query_params.multi_items():
        if k in MASK_QUERY_KEYS:
            items.append(f"{k}=<omitted>")
        else:
            vv = v if len(v) <= 80 else (v[:80] + "…")
            items.append(f"{k}={vv}")
    return "&".join(items)


def _mask_body(body_str: str, max_len: int = 500) -> str:
    """Body 문자열을 마스킹하고 길이 제한"""
    if not body_str:
        return ""

    # JSON인 경우 민감 키 마스킹
    try:
        body_dict = json.loads(body_str)
        if isinstance(body_dict, dict):
            for key in MASK_BODY_KEYS:
                if key in body_dict:
                    body_dict[key] = "<masked>"
            body_str = json.dumps(body_dict, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        pass

    # 길이 제한
    if len(body_str) > max_len:
        return body_str[:max_len] + "…(truncated)"
    return body_str


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Access 로그 + 에러 시 상세 정보 로깅"""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        status = 500
        exc_info = None
        body_str = ""

        # POST/PUT/PATCH 요청은 body 미리 읽기 (에러 로깅용)
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                body_str = body_bytes.decode("utf-8", errors="replace")
            except Exception:
                body_str = "<failed to read body>"

        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception as e:
            exc_info = e
            raise
        finally:
            ms = (time.perf_counter() - start) * 1000
            path = request.url.path
            q = _masked_query(request)

            # access 로그
            if q:
                access_logger.info("%s %s?%s -> %s (%.1fms)", request.method, path, q, status, ms)
            else:
                access_logger.info("%s %s -> %s (%.1fms)", request.method, path, status, ms)

            # 500 에러 시 상세 정보 + traceback 로깅
            if exc_info is not None:
                tb_str = "".join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))

                # 요청 정보 구성
                req_info = [
                    f"Method: {request.method}",
                    f"Path: {path}",
                ]
                if q:
                    req_info.append(f"Query: {q}")
                if body_str:
                    req_info.append(f"Body: {_mask_body(body_str)}")

                app_logger.error(
                    "Unhandled exception in %s %s\n"
                    "=== Request Info ===\n%s\n"
                    "=== Traceback ===\n%s",
                    request.method,
                    path,
                    "\n".join(req_info),
                    tb_str
                )


