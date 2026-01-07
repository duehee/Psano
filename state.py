from fastapi import APIRouter
from schemas import StateResponse
from storage import GLOBAL_STATE

router = APIRouter(tags=["state"])

@router.get("", response_model=StateResponse)
def state():
    return {
        "stage": GLOBAL_STATE["stage"],
        "values": GLOBAL_STATE["values"],
        "total_teach_count": GLOBAL_STATE["total_teach_count"],
        "total_talk_count": GLOBAL_STATE["total_talk_count"],
    }