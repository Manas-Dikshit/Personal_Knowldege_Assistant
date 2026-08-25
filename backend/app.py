from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import ChatRequest, ChatResponse
from llm import mrd_ai

app = FastAPI(title="MRD AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat")
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty."
        )

    response = mrd_ai.ask(request.message)

    return ChatResponse(response=response)
