"""
main.py — FastAPI Backend
──────────────────────────
Ye server hai jo Streamlit frontend se baat karta hai.

Endpoints:
- POST /chat      → User ka message lo, agent se response lo
- POST /reset     → Conversation history clear karo
- GET  /health    → Server alive check
- GET  /files     → Drive ke saare files list karo

Kaise run karo:
    uvicorn main:app --reload --port 8000
"""

import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="TailorTalk API",
    description="Conversational Google Drive Search Agent",
    version="1.0.0"
)

# CORS — Streamlit alag port pe hoga, isliye CORS allow karo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Session Management ────────────────────────────────────────────────────────
# Har user ka alag agent instance — conversation history separate
# Production mein Redis use karte hain, abhi dictionary kaafi hai
sessions: dict = {}

def get_or_create_session(session_id: str):
    """Session id ke liye agent lo ya naya banao."""
    from agent import TailorTalkAgent
    if session_id not in sessions:
        sessions[session_id] = TailorTalkAgent()
    return sessions[session_id]


# ── Request/Response Models ───────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"   # Streamlit ek hi session use karega

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ResetRequest(BaseModel):
    session_id: str = "default"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Server alive hai kya check karo."""
    return {
        "status": "ok",
        "message": "TailorTalk backend is running",
        "llm_provider": os.getenv("LLM_PROVIDER", "groq"),
        "drive_folder": os.getenv("GOOGLE_DRIVE_FOLDER_ID", "not set")
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    User ka message lo, agent se response lo.

    Example request:
    {
        "message": "find all PDF files",
        "session_id": "user123"
    }
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    agent = get_or_create_session(request.session_id)
    response = agent.chat(request.message)

    return ChatResponse(
        response=response,
        session_id=request.session_id
    )


@app.post("/reset")
def reset_conversation(request: ResetRequest):
    """Conversation history clear karo."""
    agent = get_or_create_session(request.session_id)
    message = agent.reset()
    return {"message": message, "session_id": request.session_id}


@app.get("/files")
def list_files():
    """Drive ke saare files list karo — testing ke liye."""
    try:
        from google_drive_tool import list_all_files
        result = list_all_files.invoke("")
        return {"files": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
