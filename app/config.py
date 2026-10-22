from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    ENVIRONMENT: str = Field(default="development")
    MASTER_API_KEY: str = Field(default="ab_master_sec_9999888877776666")

    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1")

    DATABASE_PATH: str = Field(default="data/audio_brief.db")
    UPLOAD_DIR: str = Field(default="data/uploads")
    MAX_FILE_SIZE_MB: int = Field(default=50)
    WEBHOOK_TIMEOUT_SECONDS: int = Field(default=10)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def db_path(self) -> Path:
        p = Path(self.DATABASE_PATH)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def uploads_path(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
