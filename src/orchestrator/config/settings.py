from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, AnyUrl
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # LLM
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str

    # Webhooks (opcionais)
    WEBHOOK_RESUMO_URL: Optional[str] = None
    WEBHOOK_FEEDBACK_URL: Optional[str] = None
    WEBHOOK_CATEGORIA_URL: Optional[str] = None

    # LG
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str
    LANGFUSE_ENABLED: bool = True

    WORKFLOWS_API_KEY: str

    # API
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Agente Orquestrador Workflows"
    ENV: str = "dev"

    # Config do Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()