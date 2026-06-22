from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import ChatRequest, ChatResponse

from llm import mrd_ai

app = FastAPI(title="MRD AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/chat")
def chat(request: ChatRequest):

    response = mrd_ai.ask(request.message)

    return ChatResponse(
        response=response
    )