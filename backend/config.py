from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    default_provider: str = "ollama"
    default_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"

    gemini_api_key: str = ""
    groq_api_key: str = ""
    openrouter_api_key: str = ""

    host: str = "127.0.0.1"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
