from functools import lru_cache

from jubigestor.config import settings
from jubigestor.llm.base import LLMProvider
from jubigestor.llm.echo import EchoProvider
from jubigestor.llm.gemini import GeminiProvider


@lru_cache
def get_provider() -> LLMProvider:
    """Return the active LLM provider based on config (singleton)."""
    provider = settings.llm_provider.lower()

    if provider == "echo":
        return EchoProvider()

    if provider in ("auto", "gemini"):
        if settings.gemini_api_key:
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
                embedding_model=settings.gemini_embedding_model,
                embedding_dim=settings.gemini_embedding_dim,
            )
        if provider == "gemini":
            raise RuntimeError(
                "LLM_PROVIDER=gemini but GEMINI_API_KEY is missing. "
                "Set it, or use LLM_PROVIDER=auto/echo."
            )

    # auto without an API key -> fallback that keeps the app alive.
    return EchoProvider()


__all__ = ["LLMProvider", "get_provider"]
