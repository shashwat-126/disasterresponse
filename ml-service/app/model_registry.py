from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    host: str = "0.0.0.0"
    port: int = 8001
    training_data_path: str = "data/training_data.csv"
    model_path: str = "artifacts/model.pkl"
    label_encoder_path: str = "artifacts/label_encoder.pkl"
    metadata_path: str = "artifacts/metadata.json"


settings = Settings()


def ensure_parent_dirs() -> None:
    for path in [settings.model_path, settings.label_encoder_path, settings.metadata_path]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
