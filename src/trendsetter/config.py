from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://trendsetter:trendsetter@localhost:5433/trendsetter"

    scrapecreators_api_key: str = ""
    apify_token: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    fernet_key: str = ""
    app_password: str = "change-me"
    session_secret: str = "change-me-too"

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = ""
    r2_public_base_url: str = ""

    draft_model: str = "claude-sonnet-5"
    label_model: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-small"

    config_dir: Path = CONFIG_DIR


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_yaml(name: str) -> dict[str, Any]:
    """Load a config YAML by filename (e.g. 'cadence.yml') from the config dir."""
    path = get_settings().config_dir / name
    with open(path) as f:
        return yaml.safe_load(f) or {}
