
import time
import logging
from fastapi import Request

access_logger = logging.getLogger("psano.access")

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

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        ms = (time.perf_counter() - start) * 1000

        path = request.url.path
        # 제일 깔끔: path만 찍기
        # access_logger.info("%s %s -> %s (%.1fms)", request.method, path, status, ms)

        # 쿼리도 필요하면: template 같은 건 마스킹됨
        q = _masked_query(request)
        if q:
            access_logger.info("%s %s?%s -> %s (%.1fms)", request.method, path, q, status, ms)
        else:
            access_logger.info("%s %s -> %s (%.1fms)", request.method, path, status, ms)
