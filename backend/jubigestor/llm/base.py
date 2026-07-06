from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence


class LLMProvider(ABC):
    """Common contract for any LLM provider.

    Keeping this abstraction lets us switch Gemini <-> OpenAI <-> Claude by
    changing a single environment variable, without touching the routes or RAG.
    """

    name: str

    @abstractmethod
    async def generate(self, message: str, *, context: str | None = None) -> str:
        """Generate a reply for `message`, optionally grounded in `context` (RAG)."""

    @abstractmethod
    def generate_stream(
        self, message: str, *, context: str | None = None
    ) -> AsyncIterator[str]:
        """Like `generate`, but emits the reply in chunks (streaming).

        Implement as an async generator: `async def ...: yield <chunk>`.
        """

    @abstractmethod
    async def embed(
        self, texts: Sequence[str], *, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[list[float]]:
        """Return the embedding of each text.

        `task_type` tunes the embedding for its use: RETRIEVAL_DOCUMENT when
        indexing (ingestion) and RETRIEVAL_QUERY when querying. Using the right
        one improves retrieval quality.
        """
