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


settings = Settings()
