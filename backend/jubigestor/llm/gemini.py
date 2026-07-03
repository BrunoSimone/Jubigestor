from collections.abc import AsyncIterator, Sequence

from google import genai
from google.genai import types

from jubigestor.llm.base import LLMProvider
from jubigestor.llm.prompts import SYSTEM_PROMPT, build_user_prompt


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

    async def generate_stream(
        self, message: str, *, context: str | None = None
    ) -> AsyncIterator[str]:
        stream = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=build_user_prompt(message, context),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
            ),
        )
        async for chunk in stream:
            if chunk.text:
                yield chunk.text

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
