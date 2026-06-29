from abc import ABC, abstractmethod
from collections.abc import Sequence


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
    async def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Devuelve el embedding de cada texto. Se usa en el pipeline de ingesta y en retrieve."""
