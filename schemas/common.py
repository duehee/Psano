from enum import Enum
from pydantic import BaseModel

class Phase(str, Enum):
    formation = "formation"
    chat = "chat"

class Status(str, Enum):
    ok = "ok"
    fallback = "fallback"
    error = "error"

class OkResponse(BaseModel):
    ok: bool = True