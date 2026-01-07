import time
import threading
from typing import Any, Dict
from functools import wraps

_lock = threading.Lock()

GLOBAL_STATE: Dict[str, Any] = {
    "stage": 1,
    "values": {},
    "total_teach_count": 0,
    "total_talk_count": 0,
    "updated_at": time.time(),
}

SESSIONS: Dict[str, Dict[str, Any]] = {}

def with_lock(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with _lock:
            return fn(*args, **kwargs)
    return wrapper