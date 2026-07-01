from datetime import date

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    """Cita de un documento oficial usado para responder."""

    title: str
    url: str
    published_at: date | None = None


class ChatResponse(BaseModel):
    reply: str
    sources: list[Source] = []
