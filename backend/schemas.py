from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class SourceInfo(BaseModel):
    source: str
    label: str = ""
    score: float = 0.0


class ChatResponse(BaseModel):
    response: str
    sources: list[SourceInfo] = []