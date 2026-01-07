from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from health import router as health_router
from session import router as session_router
from action.teach import router as teach_router
from action.talk import router as talk_router
from state import router as state_router
from ui import router as ui_router

app = FastAPI(title="Psano MVP API", version="0.1.0")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(teach_router, prefix="/teach", tags=["teach"])
app.include_router(talk_router, prefix="/talk", tags=["talk"])
app.include_router(state_router, prefix="/state", tags=["state"])
app.include_router(ui_router, prefix="/ui", tags=["ui"])
