from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence


class LLMProvider(ABC):
    """Contrato común para cualquier proveedor de LLM.

    Mantener esta abstracción permite cambiar Gemini <-> OpenAI <-> Claude
    cambiando una sola variable de entorno, sin tocar las rutas ni el RAG.
    """

    name: str

    @abstractmethod
    async def generate(self, message: str, *, context: str | None = None) -> str:
        """Genera una respuesta para `message`, opcionalmente apoyada en `context` (RAG)."""

    @abstractmethod
    def generate_stream(
        self, message: str, *, context: str | None = None
    ) -> AsyncIterator[str]:
        """Igual que `generate`, pero emite la respuesta en chunks (streaming).

        Implementar como async generator: `async def ...: yield <chunk>`.
        """

    @abstractmethod
    async def embed(
        self, texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        """Devuelve el embedding de cada texto.

        `task_type` afina el embedding segun el uso: RETRIEVAL_DOCUMENT al indexar
        (ingesta) y RETRIEVAL_QUERY al consultar. Usar el correcto mejora el retrieve.
        """
