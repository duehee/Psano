from fastapi import APIRouter
from schemas.common import OkResponse

router = APIRouter()

@router.get("/health", response_model=OkResponse)
def health():
    return {"ok": True}