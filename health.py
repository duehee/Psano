from fastapi import APIRouter
from schemas import BasicStatusResponse

router = APIRouter(tags=["health"])

@router.get("", response_model=BasicStatusResponse)
def health():
    return {"ok": True}