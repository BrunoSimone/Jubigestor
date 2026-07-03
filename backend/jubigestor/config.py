from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno (o un archivo .env)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Proveedor de LLM activo: "auto" usa Gemini si hay API key, si no cae al echo.
    # Valores posibles: "auto" | "gemini" | "echo".
    llm_provider: str = "auto"

    # Credenciales / modelos de Gemini (Google AI Studio).
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    # Dimensiones del embedding (MRL). 768 entra holgado en el indice de pgvector
    # (limite 2000) y casi no pierde calidad. Definir ANTES de embedear el corpus:
    # cambiarlo obliga a re-embedear todo y a recrear la columna vector(N).
    gemini_embedding_dim: int = 768

    # Conexion a Postgres. Local (Docker): postgresql://jubigestor:jubigestor@localhost:5432/jubigestor
    database_url: str | None = None

    # Pipeline de ingesta (chunking). Tamaño/overlap en caracteres.
    chunk_size: int = 1200
    chunk_overlap: int = 150
    embed_batch_size: int = 50

    # RAG (retrieve). Cuántos chunks traer y el umbral de distancia coseno para
    # considerarlos relevantes: por encima se descartan y se responde sin contexto
    # (el system prompt hace que el modelo derive a ANSES en vez de inventar).
    rag_top_k: int = 4
    # Calibrado 2026-07-01 sobre el corpus real: preguntas reales ~0.22-0.26,
    # saludos/small-talk ~0.35-0.39, off-topic ~0.45+. 0.32 deja pasar solo las
    # consultas reales (un saludo NO trae citas). Revisar si el corpus crece mucho.
    rag_max_distance: float = 0.32

    # Rate limiting del chat: máximo de consultas por IP en una ventana de tiempo.
    rate_limit_requests: int = 20
    rate_limit_window_seconds: int = 60


settings = Settings()
