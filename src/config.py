from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):

    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: Optional[str] = None
    GROQ_MODEL_TEMPERATURE: Optional[float] = None
    GROQ_MODEL_MAX_TOKEN: Optional[int] = None

    LANGCHAIN_TRACING_V2: Optional[str] = "true"
    LANGCHAIN_ENDPOINT: Optional[str] = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = "Competitor_Research"

    TAVILY_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Prevents crashing if extra vars exist in .env
    )

# Create a global instance of settings to import throughout the app
@lru_cache
def get_settings() -> Settings:
    """
    Cached settings getter returning a singleton Settings instance.
    """
    return Settings()