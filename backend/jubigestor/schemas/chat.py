from datetime import date

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    """Citation of an official document used to answer."""

    title: str
    url: str
    published_at: date | None = None
