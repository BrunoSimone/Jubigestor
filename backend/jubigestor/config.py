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


settings = Settings()
