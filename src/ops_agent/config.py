from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = "sqlite:///data/ops.db"
    log_level: str = "INFO"
    data_dir: Path = Path("data")
    log_dir: Path = Path("logs")
    static_dir: Path = Path("static")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
