from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

router = APIRouter()
client = OpenAI()

class InteractionRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: str = Field(default="gpt-4.1-mini")
    max_output_tokens: int = Field(default=150, ge=1, le=2000)

class InteractionResponse(BaseModel):
    reply: str

@router.get("/health")
def health():
    return {"ok": True}

@router.post("/interaction", response_model=InteractionResponse)
def interaction(req: InteractionRequest):
    try:
        resp = client.responses.create(
            model=req.model,
            input=req.message,
            max_output_tokens=req.max_output_tokens,
        )
        return {"reply": resp.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))