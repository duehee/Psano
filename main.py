from dotenv import load_dotenv

from logging_conf import setup_logging
from middleware.access_log import AccessLogMiddleware

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import health, session, question, answer, state, talk, ui, admin, persona, monologue, test, idle, monitor, exhibit, exhibit_talk

setup_logging()
app = FastAPI(title="Psano Backend", version="0.1.0")

# CORS 설정 (TD, 브라우저 등에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (전시용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AccessLogMiddleware)

app.include_router(health.router, tags=["health"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(answer.router, prefix="/answer", tags=["answer"])
app.include_router(state.router, prefix="/state", tags=["state"])
app.include_router(talk.router, prefix="/talk", tags=["talk"])
app.include_router(ui.router, prefix="/ui", tags=["ui"])
app.include_router(test.router, prefix="/test_ui", tags=["test_ui"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(persona.router, prefix="/persona", tags=["persona"])
app.include_router(monologue.router, prefix="/monologue", tags=["monologue"])
app.include_router(idle.router, prefix="/idle", tags=["idle"])
app.include_router(monitor.router, prefix="/monitor", tags=["monitor"])
app.include_router(exhibit.router, prefix="/exhibit_teach", tags=["exhibit"])
app.include_router(exhibit_talk.router, prefix="/exhibit_talk", tags=["exhibit"])