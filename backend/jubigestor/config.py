from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables (or a .env file)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Active LLM provider: "auto" uses Gemini if an API key is present, else echo.
    # Allowed values: "auto" | "gemini" | "echo".
    llm_provider: str = "auto"

    # Gemini credentials / models (Google AI Studio).
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    # Embedding dimensions (MRL). 768 stays well under pgvector's index limit
    # (2000) with negligible quality loss. Freeze this BEFORE embedding the corpus:
    # changing it forces a full re-embed and recreating the vector(N) column.
    gemini_embedding_dim: int = 768

    # Postgres connection. Local (Docker): postgresql://jubigestor:jubigestor@localhost:5432/jubigestor
    database_url: str | None = None

    # CORS: comma-separated list of origins allowed to call the API.
    # "*" is fine for local dev; set the real frontend domain(s) in production.
    allowed_origins: str = "*"

    # Ingestion pipeline (chunking). Size/overlap measured in characters.
    chunk_size: int = 1200
    chunk_overlap: int = 150
    embed_batch_size: int = 50

    # RAG (retrieve). How many chunks to fetch and the cosine-distance threshold
    # to consider them relevant: anything above is dropped and we answer without
    # context (the system prompt then defers to ANSES instead of hallucinating).
    rag_top_k: int = 4
    # Recalibrated 2026-07-06 on the 13-doc / 28-chunk corpus: genuine questions
    # land at ~0.22-0.31, greetings ~0.37-0.38, off-topic ~0.39-0.43. There is a
    # clean gap at 0.31-0.37; 0.34 gives valid queries headroom while still keeping
    # greetings/off-topic out (no spurious citations). Revisit as the corpus grows.
    rag_max_distance: float = 0.34

    # Chat rate limiting: max requests per IP within a time window.
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60


settings = Settings()
