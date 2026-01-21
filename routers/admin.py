from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
import os
from typing import Optional, Dict

from fastapi import APIRouter, Depends, Query, HTTPException, File, UploadFile, Header
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from routers.persona import _generate_persona
from schemas.admin import (
    AdminSessionsResponse, AdminProgressResponse,
    AdminResetRequest, AdminResetResponse,
    AdminPhaseSetRequest, AdminPhaseSetResponse,
    AdminSetCurrentQuestionRequest, AdminSetCurrentQuestionResponse,
    ImportErrorItem, AdminQuestionsImportResponse, AdminSettingsImportResponse,
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


# =========================
# 공통 유틸리티
# =========================

def _iso(dt):
    if dt is None:
        return None
    try:
        return dt.isoformat(sep=" ", timespec="seconds")
    except Exception:
        return str(dt)


def now_kst():
    return datetime.utcnow() + timedelta(hours=9)


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


def _check_admin_token(x_admin_token: Optional[str]) -> None:
    """ADMIN_TOKEN 환경변수가 설정된 경우에만 토큰 검증"""
    if not ADMIN_TOKEN:
        return
    if not x_admin_token or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized (invalid admin token)")


# =========================
# 엑셀 파싱 유틸리티
# =========================

def _cell_str(ws, col: str, row: int) -> str:
    try:
        v = ws[f"{col}{row}"].value
        return "" if v is None else str(v).strip()
    except Exception:
        return ""


def _cell_int(ws, col: str, row: int) -> Optional[int]:
    try:
        v = ws[f"{col}{row}"].value
        if v is None or str(v).strip() == "":
            return None
        return int(v)
    except Exception:
        return None


def _cell_float(ws, col: str, row: int) -> Optional[float]:
    try:
        v = ws[f"{col}{row}"].value
        if v is None or str(v).strip() == "":
            return None
        return float(v)
    except Exception:
        return None


def _get_sheet(wb, preferred_names: list[str]):
    """워크북에서 선호하는 이름의 시트 찾기"""
    name_map = {ws.title.strip().lower(): ws for ws in wb.worksheets}
    for n in preferred_names:
        ws = name_map.get(n.strip().lower())
        if ws is not None:
            return ws
    return None


def _parse_enabled(raw: str) -> Optional[int]:
    s = (raw or "").strip().upper()
    if s in ("Y", "1", "TRUE", "T"):
        return 1
    if s in ("N", "0", "FALSE", "F"):
        return 0
    return None


# =========================
# Questions Import
# =========================

# 컬럼 매핑 (questions 시트)
Q_COL_ID = "A"
Q_COL_VALUE_A = "D"
Q_COL_VALUE_B = "E"
Q_COL_AXIS_KO = "F"
Q_COL_QUESTION = "H"
Q_COL_CHOICE_A = "I"
Q_COL_CHOICE_B = "J"
Q_COL_ENABLED = "K"

AXIS_MAP: Dict[str, str] = {
    "나의 길": "My way",
    "새로움": "Newness",
    "지금 이 순간": "This moment",
    "성장": "growth",
    "함께": "together",
}

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
    POST /admin/questions/import
    xlsx 업로드로 questions upsert.
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

    upsert_sql = text("""
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
    """)

    try:
        for r in range(2, ws.max_row + 1):
            id_val = _cell_int(ws, Q_COL_ID, r)
            q_text = _cell_str(ws, Q_COL_QUESTION, r)

            if id_val is None and q_text == "":
                continue

            result.processed += 1

            axis_ko = _cell_str(ws, Q_COL_AXIS_KO, r)
            axis_key = _map_axis_key(axis_ko)
            choice_a = _cell_str(ws, Q_COL_CHOICE_A, r)
            choice_b = _cell_str(ws, Q_COL_CHOICE_B, r)
            value_a_key = _cell_str(ws, Q_COL_VALUE_A, r)
            value_b_key = _cell_str(ws, Q_COL_VALUE_B, r)
            enabled_raw = _cell_str(ws, Q_COL_ENABLED, r)
            enabled = _parse_enabled(enabled_raw)

            # 필수값 검증
            if id_val is None:
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Invalid or missing ID (A column)"))
                continue
            if not axis_key:
                result.failed += 1
                result.errors.append(ImportErrorItem(
                    row=r, message=f"Invalid axis (F column). Got '{axis_ko}'. Expected: {list(AXIS_MAP.keys())}"
                ))
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
                result.errors.append(ImportErrorItem(
                    row=r, message=f"Invalid enabled (K column). Got '{enabled_raw}', expected Y/N"
                ))
                continue

            params = {
                "id": id_val,
                "axis_key": axis_key,
                "question_text": q_text,
                "choice_a": choice_a,
                "choice_b": choice_b,
                "enabled": enabled,
                "value_a_key": value_a_key if value_a_key else None,
                "value_b_key": value_b_key if value_b_key else None,
            }

            res = db.execute(upsert_sql, params)
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


# =========================
# Settings (Growth Stages) Import
# =========================

# 컬럼 매핑 (settings 시트)
S_COL_STAGE_ID = "A"
S_COL_NAME_KR = "B"
S_COL_NAME_EN = "C"
S_COL_MIN_ANSWERS = "D"
S_COL_MAX_ANSWERS = "E"
S_COL_METAPHOR = "F"
S_COL_CERTAINTY = "G"
S_COL_SENT_LEN = "H"
S_COL_EMPATHY = "I"
S_COL_NOTES = "J"


@router.post("/settings/import", response_model=AdminSettingsImportResponse)
async def admin_settings_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    """
    POST /admin/settings/import
    xlsx 업로드로 psano_growth_stages upsert.
    """
    _check_admin_token(x_admin_token)

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        wb = load_workbook(filename=BytesIO(content), data_only=True)
        ws = _get_sheet(wb, ["setting", "settings", "stage", "stages"]) or wb.worksheets[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid xlsx file: {e}")

    result = AdminSettingsImportResponse()

    upsert_sql = text("""
        INSERT INTO psano_growth_stages
            (stage_id, stage_name_kr, stage_name_en,
             min_answers, max_answers,
             metaphor_density, certainty,
             sentence_length, empathy_level, notes)
        VALUES
            (:stage_id, :stage_name_kr, :stage_name_en,
             :min_answers, :max_answers,
             :metaphor_density, :certainty,
             :sentence_length, :empathy_level, :notes)
        ON DUPLICATE KEY UPDATE
            stage_name_kr    = VALUES(stage_name_kr),
            stage_name_en    = VALUES(stage_name_en),
            min_answers      = VALUES(min_answers),
            max_answers      = VALUES(max_answers),
            metaphor_density = VALUES(metaphor_density),
            certainty        = VALUES(certainty),
            sentence_length  = VALUES(sentence_length),
            empathy_level    = VALUES(empathy_level),
            notes            = VALUES(notes)
    """)

    try:
        for r in range(2, ws.max_row + 1):
            sid = _cell_int(ws, S_COL_STAGE_ID, r)
            name_kr = _cell_str(ws, S_COL_NAME_KR, r)
            name_en = _cell_str(ws, S_COL_NAME_EN, r)

            if sid is None and name_kr == "" and name_en == "":
                continue

            result.processed += 1

            min_a = _cell_int(ws, S_COL_MIN_ANSWERS, r)
            max_a = _cell_int(ws, S_COL_MAX_ANSWERS, r)
            metaphor = _cell_float(ws, S_COL_METAPHOR, r)
            certainty = _cell_float(ws, S_COL_CERTAINTY, r)
            sent_len = _cell_str(ws, S_COL_SENT_LEN, r)
            empathy = _cell_float(ws, S_COL_EMPATHY, r)
            notes = _cell_str(ws, S_COL_NOTES, r)

            # 필수값 검증
            if sid is None:
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing/invalid stage_id (A column)"))
                continue
            if name_kr == "" or name_en == "":
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing stage_name_kr(B) or stage_name_en(C)"))
                continue
            if min_a is None or max_a is None:
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing min_answers(D) or max_answers(E)"))
                continue
            if metaphor is None or certainty is None or empathy is None:
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing metaphor(F) / certainty(G) / empathy(I)"))
                continue
            if sent_len == "":
                result.failed += 1
                result.errors.append(ImportErrorItem(row=r, message="Missing sentence_length(H)"))
                continue

            params = {
                "stage_id": sid,
                "stage_name_kr": name_kr,
                "stage_name_en": name_en,
                "min_answers": min_a,
                "max_answers": max_a,
                "metaphor_density": metaphor,
                "certainty": certainty,
                "sentence_length": sent_len,
                "empathy_level": empathy,
                "notes": notes if notes else None,
            }

            res = db.execute(upsert_sql, params)
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


# =========================
# 세션/진행률 조회
# =========================

@router.get("/sessions", response_model=AdminSessionsResponse)
def list_sessions(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    total_row = db.execute(text("SELECT COUNT(*) AS cnt FROM sessions")).mappings().first()
    total = int(total_row["cnt"]) if total_row else 0

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

        sessions = [{
            "id": int(r["id"]),
            "visitor_name": r["visitor_name"],
            "started_at": _iso(r["started_at"]),
            "ended_at": _iso(r["ended_at"]),
            "end_reason": r.get("end_reason"),
        } for r in rows]

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

        sessions = [{
            "id": int(r["id"]),
            "visitor_name": r["visitor_name"],
            "started_at": _iso(r["started_at"]),
            "ended_at": _iso(r["ended_at"]),
            "end_reason": None,
        } for r in rows]

    return {"total": total, "sessions": sessions}


@router.get("/progress", response_model=AdminProgressResponse)
def get_progress(db: Session = Depends(get_db)):
    st = db.execute(
        text("SELECT phase, current_question FROM psano_state WHERE id = 1")
    ).mappings().first()

    if not st:
        raise HTTPException(status_code=500, detail="psano_state(id=1) not found")

    phase = st["phase"]
    if phase not in ("teach", "talk"):
        phase = "teach"

    current_q = int(st["current_question"])
    answered = MAX_QUESTIONS if phase == "talk" else max(0, min(MAX_QUESTIONS, current_q - 1))
    ratio = float(answered) / float(MAX_QUESTIONS) if MAX_QUESTIONS > 0 else 0.0

    return {
        "phase": phase,
        "current_question": current_q,
        "answered_count": answered,
        "max_questions": MAX_QUESTIONS,
        "progress_ratio": ratio,
    }


# =========================
# 상태 관리 (Reset, Phase, Question)
# =========================

@router.post("/reset", response_model=AdminResetResponse)
def admin_reset(req: AdminResetRequest, db: Session = Depends(get_db)):
    """초기화: state, answers, sessions, personality"""

    def _reset_table(table_name: str):
        db.execute(text(f"DELETE FROM {table_name}"))
        db.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))

    try:
        ensure_psano_state_row(db)

        if req.reset_answers:
            _reset_table("answers")

        if req.reset_sessions:
            try:
                _reset_table("talk_messages")
            except Exception:
                pass
            _reset_table("sessions")

        if req.reset_personality:
            db.execute(text("""
                UPDATE psano_personality
                SET self_direction = 0, conformity = 0, stimulation = 0, security = 0,
                    hedonism = 0, tradition = 0, achievement = 0, benevolence = 0,
                    power = 0, universalism = 0
                WHERE id = 1
            """))

        if req.reset_state:
            try:
                db.execute(text("""
                    UPDATE psano_state
                    SET phase = 'teach', current_question = 1,
                        formed_at = NULL, persona_prompt = NULL, values_summary = NULL
                    WHERE id = 1
                """))
            except Exception:
                db.execute(text("""
                    UPDATE psano_state
                    SET phase = 'teach', current_question = 1
                    WHERE id = 1
                """))

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
    """테스트용 phase 강제 변경"""
    if req.phase not in ("teach", "talk"):
        raise HTTPException(status_code=400, detail="invalid phase")

    try:
        ensure_psano_state_row(db)

        if req.phase == "teach":
            try:
                db.execute(text("UPDATE psano_state SET phase = 'teach', formed_at = NULL WHERE id = 1"))
            except Exception:
                db.execute(text("UPDATE psano_state SET phase = 'teach' WHERE id = 1"))
        else:
            try:
                db.execute(
                    text("UPDATE psano_state SET phase = 'talk', formed_at = :formed_at WHERE id = 1"),
                    {"formed_at": now_kst()}
                )
            except Exception:
                db.execute(text("UPDATE psano_state SET phase = 'talk' WHERE id = 1"))

        db.commit()
        return AdminPhaseSetResponse(ok=True, phase=req.phase)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")


@router.post("/state/set_current_question", response_model=AdminSetCurrentQuestionResponse)
def admin_set_current_question(req: AdminSetCurrentQuestionRequest, db: Session = Depends(get_db)):
    """테스트용 현재 질문 강제 설정"""
    try:
        ensure_psano_state_row(db)
        db.execute(
            text("UPDATE psano_state SET current_question = :q WHERE id = 1"),
            {"q": int(req.current_question)}
        )
        db.commit()
        return AdminSetCurrentQuestionResponse(ok=True, current_question=int(req.current_question))

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")


# =========================
# Persona 생성 (관리자용)
# =========================

@router.post("/generate", response_model=PersonaGenerateResponse)
def admin_persona_generate(req: PersonaGenerateRequest, db: Session = Depends(get_db)):
    """관리자 테스트용: 380 미만이어도 페르소나 생성 가능"""
    try:
        return _generate_persona(db, force=req.force, model=req.model, allow_under_380=True)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"admin persona generate failed: {e}")