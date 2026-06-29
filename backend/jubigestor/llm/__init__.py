from functools import lru_cache

from jubigestor.config import settings
from jubigestor.llm.base import LLMProvider
from jubigestor.llm.echo import EchoProvider
from jubigestor.llm.gemini import GeminiProvider


@lru_cache
def get_provider() -> LLMProvider:
    """Devuelve el proveedor de LLM activo según la config (singleton)."""
    provider = settings.llm_provider.lower()

    if provider == "echo":
        return EchoProvider()

    if provider in ("auto", "gemini"):
        if settings.gemini_api_key:
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model=settings.gemini_model,
                embedding_model=settings.gemini_embedding_model,
            )
        if provider == "gemini":
            raise RuntimeError(
                "LLM_PROVIDER=gemini pero falta GEMINI_API_KEY. "
                "Configurala o usá LLM_PROVIDER=auto/echo."
            )

    # auto sin API key -> fallback que mantiene la app viva.
    return EchoProvider()


__all__ = ["LLMProvider", "get_provider"]
