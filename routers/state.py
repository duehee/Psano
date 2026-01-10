from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.state import StateResponse
from database import get_db  # 너 프로젝트 경로에 맞춰

router = APIRouter()

@router.get("", response_model=StateResponse)
def get_state(db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT phase, current_question, formed_at
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    formed_at = row["formed_at"]
    formed_iso = formed_at.isoformat() if formed_at is not None else None

    return {
        "phase": row["phase"],
        "current_question": int(row["current_question"]),
        "formed_at": formed_iso,
    }