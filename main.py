from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers import health, session, question, answer, state, talk, ui, admin, persona, monologue, test

app = FastAPI(title="Psano Backend", version="0.1.0")

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