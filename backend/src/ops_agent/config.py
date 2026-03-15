from pathlib import Path

from pydantic_settings import BaseSettings

# Anchor to backend/ directory: config.py → ops_agent/ → src/ → backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    database_url: str = f"sqlite:///{BACKEND_DIR / 'data' / 'ops.db'}"
    log_level: str = "INFO"
    data_dir: Path = BACKEND_DIR / "data"
    log_dir: Path = BACKEND_DIR / "logs"
    static_dir: Path = BACKEND_DIR / "static"

    model_config = {
        "env_file": (str(BACKEND_DIR.parent / ".env"), ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
