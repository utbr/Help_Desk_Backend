from typing import List, Optional
from pydantic import PostgresDsn, AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: Optional[PostgresDsn] = None
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)
    OPENAI_API_KEY: Optional[str] = None  
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   
    )

settings = Settings()