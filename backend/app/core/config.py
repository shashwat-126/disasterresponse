from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "EADRP Backend"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    database_url: str = "postgresql+psycopg://eadrp:eadrp_password@localhost:5432/eadrp"
    ml_service_url: str = "http://localhost:8001"
    cors_origins: List[str] | str = ["http://localhost:5173"]

    upload_dir: str = "uploads"
    max_upload_size_mb: int = 25

    admin_email: str = "admin@eadrp.com"
    admin_password: str = "Admin@1234"
    admin_full_name: str = "System Admin"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
