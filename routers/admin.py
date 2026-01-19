from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
import os
from typing import Optional, Dict, List

from fastapi import APIRouter, Depends, Query, HTTPException, File, UploadFile, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from routers.persona import _generate_persona
from schemas.admin import (
    AdminSessionsResponse, AdminProgressResponse,
    AdminResetRequest, AdminResetResponse,
    AdminPhaseSetRequest, AdminPhaseSetResponse,
    AdminSetCurrentQuestionRequest, AdminSetCurrentQuestionResponse,
)
from schemas.persona import PersonaGenerateResponse, PersonaGenerateRequest

try:
    from openpyxl import load_workbook
except ImportError:
    raise RuntimeError("openpyxl is required. Install with: pip install openpyxl")


router = APIRouter()

MAX_QUESTIONS = 380

# (선택) 최소 인증 토큰: 환경변수 ADMIN_TOKEN 설정 시 강제
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)


def ensure_psano_state_row(db: Session):
    row = db.execute(text("SELECT id FROM psano_state WHERE id=1")).mappings().first()
    if row:
        return

    db.execute(
        text("""
            INSERT INTO psano_state (id, phase, current_question)
            VALUES (1, 'teach', 1)
        """)
    )


def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


def _check_admin_token(x_admin_token: Optional[str]) -> None:
    if not ADMIN_TOKEN:
        return
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized (invalid admin token)")


# =========================
# /admin/questions/import 용 스키마/유틸
# =========================

AXIS_MAP: Dict[str, str] = {
    "나의 길": "My way",
    "새로움": "Newness",
    "지금 이 순간": "This moment",
    "성장": "growth",
    "함께": "together",
}

# 컬럼 레터 매핑 (너가 준 엑셀 기준)
COL_ID = "A"            # ID
COL_AXIS_KO = "F"       # 주제 한글 -> axis_key (AXIS_MAP)
COL_QUESTION = "H"      # 질문 -> question_text
COL_VALUE_A = "D"       # 가치_A -> value_a_key
COL_VALUE_B = "E"       # 가치_B -> value_b_key
COL_CHOICE_A = "I"      # 선택지_A -> choice_a
COL_CHOICE_B = "J"      # 선택지_B -> choice_b
COL_ENABLED = "K"       # 활성화(Y/N) -> enabled

class ImportErrorItem(BaseModel):
    row: int
    message: str

class AdminQuestionsImportResponse(BaseModel):
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0
    errors: List[ImportErrorItem] = Field(default_factory=list)

def _cell_str(ws, col: str, row: int) -> str:
    v = ws[f"{col}{row}"].value
    if v is None:
        return ""
    return str(v).strip()


def _cell_int(ws, col: str, row: int) -> Optional[int]:
    v = ws[f"{col}{row}"].value
    if v is None or str(v).strip() == "":
        return None
    try:
        return int(v)
    except Exception:
        return None


def _parse_enabled(raw: str) -> Optional[int]:
    s = (raw or "").strip().upper()
    if s == "Y":
        return 1
    if s == "N":
        return 0
    if s in ("1", "TRUE", "T"):
        return 1
    if s in ("0", "FALSE", "F"):
        return 0
    return None


def _map_axis_key(axis_ko: str) -> Optional[str]:
    k = (axis_ko or "").strip()
    if not k:
        return None
    if k in AXIS_MAP:
        return AXIS_MAP[k]
    if k in AXIS_MAP.values():
        return k
    return None


@router.post("/questions/import", response_model=AdminQuestionsImportResponse)
async def admin_questions_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    """
    POST /admin/questions/import (라우터가 /admin prefix로 include된다는 가정)

    xlsx 업로드로 questions upsert.
    매핑:
      A: id
      F: 주제 한글 -> axis_key (AXIS_MAP)
      H: question_text
      I: choice_a
      D: value_a_key
      J: choice_b
      E: value_b_key
      K: enabled (Y/N -> 1/0)
    """
    _check_admin_token(x_admin_token)

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        wb = load_workbook(filename=BytesIO(content), data_only=True)
        ws = wb.active
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid xlsx file: {e}")

    result = AdminQuestionsImportResponse()

    upsert_sql = text(
        """
        INSERT INTO questions
            (id, axis_key, question_text, choice_a, choice_b, enabled, value_a_key, value_b_key)
        VALUES
            (:id, :axis_key, :question_text, :choice_a, :choice_b, :enabled, :value_a_key, :value_b_key)
        ON DUPLICATE KEY UPDATE
            axis_key = VALUES(axis_key),
            question_text = VALUES(question_text),
            choice_a = VALUES(choice_a),
            choice_b = VALUES(choice_b),
            enabled = VALUES(enabled),
            value_a_key = VALUES(value_a_key),
            value_b_key = VALUES(value_b_key)
        """
    )

    try:
        # 1행은 헤더라고 가정
        for r in range(2, ws.max_row + 1):
            id_val = _cell_int(ws, COL_ID, r)
            q_text = _cell_str(ws, COL_QUESTION, r)

            # 완전 빈 줄 스킵(기준: A/H 둘 다 비면)
            if id_val is None and q_text == "":
                continue

            result.processed += 1

            axis_ko = _cell_str(ws, COL_AXIS_KO, r)
            axis_key = _map_axis_key(axis_ko)

            choice_a = _cell_str(ws, COL_CHOICE_A, r)
            choice_b = _cell_str(ws, COL_CHOICE_B, r)
            value_a_key = _cell_str(ws, COL_VALUE_A, r)
            value_b_key = _cell_str(ws, COL_VALUE_B, r)
            enabled_raw = _cell_str(ws, COL_ENABLED, r)
            enabled = _parse_enabled(enabled_raw)

            # 필수값 검증
            if id_val is None:
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Invalid or missing ID (A column)"))
                continue
            if not axis_key:
                result.failed += 1
                result.errors.append(
                    ImportErrorItem(
                        row=r,
                        message=f"Invalid axis (F column). Got '{axis_ko}'. Expected: {list(AXIS_MAP.keys())}",
                    )
                )
                continue
            if q_text == "":
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing question_text (H column)"))
                continue
            if choice_a == "" or choice_b == "":
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing choice_a(I) or choice_b(J)"))
                continue
            if enabled is None:
                result.failed += 1
                result.errors.append(
                    ImportErrorItem(row=r, message=f"Invalid enabled (K column). Got '{enabled_raw}', expected Y/N")
                )
                continue

            params = {
                "id": id_val,
                "axis_key": axis_key,
                "question_text": q_text,
                "choice_a": choice_a,
                "choice_b": choice_b,
                "enabled": enabled,
                "value_a_key": value_a_key if value_a_key != "" else None,
                "value_b_key": value_b_key if value_b_key != "" else None,
            }

            res = db.execute(upsert_sql, params)

            # 보통 insert=1, update=2, no-op=0
            if res.rowcount == 1:
                result.inserted += 1
            elif res.rowcount == 2:
                result.updated += 1
            else:
                result.unchanged += 1

        db.commit()
        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")


@router.get("/sessions", response_model=AdminSessionsResponse)
def list_sessions(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    total_row = db.execute(text("SELECT COUNT(*) AS cnt FROM sessions")).mappings().first()
    total = int(total_row["cnt"]) if total_row else 0

    # end_reason 컬럼이 있을 수도/없을 수도 있으니 fallback 쿼리
    try:
        rows = db.execute(
            text("""
                SELECT id, visitor_name, started_at, ended_at, end_reason
                FROM sessions
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        ).mappings().all()

        sessions = []
        for r in rows:
            sessions.append({
                "id": int(r["id"]),
                "visitor_name": r["visitor_name"],
                "started_at": _iso(r["started_at"]),
                "ended_at": _iso(r["ended_at"]),
                "end_reason": r.get("end_reason"),
            })

    except Exception:
        rows = db.execute(
            text("""
                SELECT id, visitor_name, started_at, ended_at
                FROM sessions
                ORDER BY started_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        ).mappings().all()

        sessions = []
        for r in rows:
            sessions.append({
                "id": int(r["id"]),
                "visitor_name": r["visitor_name"],
                "started_at": _iso(r["started_at"]),
                "ended_at": _iso(r["ended_at"]),
                "end_reason": None,
            })

    return {"total": total, "sessions": sessions}


@router.get("/progress", response_model=AdminProgressResponse)
def get_progress(db: Session = Depends(get_db)):
    st = db.execute(
        text("""
            SELECT phase, current_question
            FROM psano_state
            WHERE id = 1
        """)
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    phase = st["phase"]
    if phase not in ("teach", "talk"):
        phase = "teach"

    current_q = int(st["current_question"])

    if phase == "teach":
        answered = max(0, min(MAX_QUESTIONS, current_q - 1))
    else:
        answered = MAX_QUESTIONS

    ratio = 0.0 if MAX_QUESTIONS <= 0 else float(answered) / float(MAX_QUESTIONS)

    return {
        "phase": phase,
        "current_question": current_q,
        "answered_count": answered,
        "max_questions": MAX_QUESTIONS,
        "progress_ratio": ratio,
    }


@router.post("/reset", response_model=AdminResetResponse)
def admin_reset(req: AdminResetRequest, db: Session = Depends(get_db)):
    """
    - 기본: reset_state만 True (teach + 1번 질문으로)
    - reset_answers: answers 전체 삭제
    - reset_sessions: sessions 전체 삭제
    - reset_personality: psano_personality 10축 초기화(0)
    """
    try:
        ensure_psano_state_row(db)

        if req.reset_answers:
            db.execute(text("DELETE FROM answers ALTER TABLE answers AUTO_INCREMENT = 1;"))

        if req.reset_sessions:
            db.execute(text("DELETE FROM sessions ALTER TABLE sessions AUTO_INCREMENT = 1;"))

        if req.reset_personality:
            # id=1 row가 있다고 가정. 없을 수 있으면 insert 로직을 추가해도 됨.
            db.execute(text("""
                UPDATE psano_personality
                SET self_direction = 0,
                    conformity = 0,
                    stimulation = 0,
                    security = 0,
                    hedonism = 0,
                    tradition = 0,
                    achievement = 0,
                    benevolence = 0,
                    power = 0,
                    universalism = 0
                WHERE id = 1
            """))

        if req.reset_state:
            # 컬럼이 있을 수도/없을 수도 있으니 안전하게 처리
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'teach',
                            current_question = 1,
                            formed_at = NULL,
                            persona_prompt = NULL,
                            values_summary = NULL
                        WHERE id = 1
                    """)
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'teach',
                            current_question = 1
                        WHERE id = 1
                    """)
                )

        db.commit()
        return AdminResetResponse(
            ok=True,
            reset_answers=req.reset_answers,
            reset_sessions=req.reset_sessions,
            reset_state=req.reset_state,
            reset_personality=req.reset_personality
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")


@router.post("/phase/set", response_model=AdminPhaseSetResponse)
def admin_set_phase(req: AdminPhaseSetRequest, db: Session = Depends(get_db)):
    """
    테스트용 phase 강제 변경.
    - teach: formed_at NULL 처리(가능하면)
    - talk: formed_at 현재시간 기록(가능하면)
    """
    if req.phase not in ("teach", "talk"):
        raise HTTPException(status_code=400, detail="invalid phase")

    try:
        ensure_psano_state_row(db)

        if req.phase == "teach":
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'teach',
                            formed_at = NULL
                        WHERE id = 1
                    """)
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'teach'
                        WHERE id = 1
                    """)
                )
        else:
            try:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'talk',
                            formed_at = :formed_at
                        WHERE id = 1
                    """),
                    {"formed_at": now_kst()},
                )
            except Exception:
                db.execute(
                    text("""
                        UPDATE psano_state
                        SET phase = 'talk'
                        WHERE id = 1
                    """)
                )

        db.commit()
        return AdminPhaseSetResponse(ok=True, phase=req.phase)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")


@router.post("/state/set_current_question", response_model=AdminSetCurrentQuestionResponse)
def admin_set_current_question(req: AdminSetCurrentQuestionRequest, db: Session = Depends(get_db)):
    """
    테스트용 현재 질문 강제 설정.
    """
    try:
        ensure_psano_state_row(db)

        db.execute(
            text("""
                UPDATE psano_state
                SET current_question = :q
                WHERE id = 1
            """),
            {"q": int(req.current_question)},
        )
        db.commit()

        return AdminSetCurrentQuestionResponse(ok=True, current_question=int(req.current_question))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

@router.post("/generate", response_model=PersonaGenerateResponse)
def admin_persona_generate(req: PersonaGenerateRequest, db: Session = Depends(get_db)):
    # 관리자 테스트용: force=True면 380 미만이어도 생성 가능
    try:
        return _generate_persona(
            db,
            force=req.force,
            model=req.model,
            allow_under_380=True,   # ✅ 어드민은 테스트 허용
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"admin persona generate failed: {e}")