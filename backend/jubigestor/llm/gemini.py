from collections.abc import AsyncIterator, Sequence

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from jubigestor.llm.base import LLMProvider
from jubigestor.llm.prompts import SYSTEM_PROMPT, build_user_prompt

# Códigos HTTP transitorios: vale la pena reintentar (rate limit, saturación pasajera).
_TRANSIENT_CODES = {429, 500, 502, 503, 504}


def _is_transient(exc: BaseException) -> bool:
    """True si el fallo del LLM es transitorio (reintentable), no definitivo."""
    if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
        return True
    if isinstance(exc, genai_errors.APIError):
        return getattr(exc, "code", None) in _TRANSIENT_CODES
    return False


# Reintenta hasta 3 veces con backoff exponencial + jitter ante errores transitorios.
# NO reintenta errores definitivos (400/401/422): esos no se arreglan reintentando.
_retry_transient = retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=0.5, max=8.0),
    reraise=True,
)


class GeminiProvider(LLMProvider):
    """Proveedor basado en Google Gemini (Google AI Studio, free tier).

    Modelo por defecto: gemini-2.5-flash. El ID se inyecta desde config, así que
    migrar (p. ej. a gemini-3.5-flash) es cambiar una env var.
    """

    name = "gemini"

    def __init__(
        self, api_key: str, model: str, embedding_model: str, embedding_dim: int
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._embedding_model = embedding_model
        self._embedding_dim = embedding_dim

    @_retry_transient
    async def generate(self, message: str, *, context: str | None = None) -> str:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=build_user_prompt(message, context),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
            ),
        )
        return (response.text or "").strip()

    @_retry_transient
    async def _open_stream(self, message: str, context: str | None):
        """Abre el stream con Gemini. El retry va acá (antes del primer token),
        no sobre la iteración: reintentar a mitad de stream duplicaría texto."""
        return await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=build_user_prompt(message, context),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
            ),
        )

    async def generate_stream(
        self, message: str, *, context: str | None = None
    ) -> AsyncIterator[str]:
        stream = await self._open_stream(message, context)
        async for chunk in stream:
            if chunk.text:
                yield chunk.text

    @_retry_transient
    async def embed(
        self, texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        response = await self._client.aio.models.embed_content(
            model=self._embedding_model,
            contents=list(texts),
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self._embedding_dim,
            ),
        )
        return [list(embedding.values) for embedding in response.embeddings]
