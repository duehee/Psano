from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from schemas.state import StateResponse
from database import get_db
from util.constants import VALUE_KEYS_ORDERED, TALK_UNLOCK_THRESHOLD

router = APIRouter()

VALUE_KEYS = VALUE_KEYS_ORDERED

@router.get("", response_model=StateResponse)
def get_state(db: Session = Depends(get_db)):
    # 1) psano_state 가져오기
    #    persona_prompt 컬럼이 있을 수도/없을 수도 있으니 try로 안전 처리
    try:
        row = db.execute(
            text("""
                SELECT phase, current_question, formed_at, persona_prompt
                FROM psano_state
                WHERE id = 1
            """)
        ).mappings().first()
    except Exception:
        row = db.execute(
            text("""
                SELECT phase, current_question, formed_at
                FROM psano_state
                WHERE id = 1
            """)
        ).mappings().first()

    if not row:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    formed_at = row.get("formed_at")
    formed_iso = formed_at.isoformat() if formed_at is not None else None

    # 2) phase 값 (teach / talk)
    phase_out = (row.get("phase") or "").strip()
    if phase_out not in ("teach", "talk"):
        phase_out = "teach"  # 알 수 없는 값이면 teach로 fallback

    # 3) answered_total (누적 답변 수)
    cnt_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM answers")
    ).mappings().first()
    answered_total = int(cnt_row["cnt"]) if cnt_row else 0

    # 4) axis_scores(10) from psano_personality(id=1)
    cols_sql = ", ".join([f"`{k}`" for k in VALUE_KEYS])
    pr = db.execute(
        text(f"""
            SELECT {cols_sql}
            FROM psano_personality
            WHERE id = 1
        """)
    ).mappings().first()

    axis_scores = {}
    for k in VALUE_KEYS:
        axis_scores[k] = int((pr or {}).get(k) or 0)

    # 5) talk_unlocked
    talk_unlocked = (phase_out == "talk") or (answered_total >= TALK_UNLOCK_THRESHOLD)

    return {
        "phase": phase_out,
        "current_question": int(row["current_question"]),
        "answered_total": answered_total,
        "axis_scores": axis_scores,
        "talk_unlocked": talk_unlocked,
        "formed_at": formed_iso,
        "persona_prompt": row.get("persona_prompt") if "persona_prompt" in row else None,
    }
