
import time
import logging
import traceback
from fastapi import Request

access_logger = logging.getLogger("psano.access")
app_logger = logging.getLogger("psano")

MASK_QUERY_KEYS = {"template"}  # 여기에 마스킹할 키 추가

def _masked_query(request: Request) -> str:
    items = []
    for k, v in request.query_params.multi_items():
        if k in MASK_QUERY_KEYS:
            items.append(f"{k}=<omitted>")
        else:
            vv = v if len(v) <= 80 else (v[:80] + "…")
            items.append(f"{k}={vv}")
    return "&".join(items)

async def access_log_middleware(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    exc_info = None

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    except Exception as e:
        # 예외 정보 저장 (finally에서 로깅)
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

        # 500 에러 시 상세 traceback을 app.log에 기록
        if exc_info is not None:
            tb_str = "".join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__))
            app_logger.error(
                "Unhandled exception in %s %s\n%s",
                request.method,
                path,
                tb_str
            )
