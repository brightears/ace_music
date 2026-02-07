"""Configuration management for ACE Music platform."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    All ACE-Step API connection parameters are configured here.
    Copy .env.example to .env and fill in your values.
    """

    # ACE-Step API connection
    acestep_api_url: str = "http://localhost:8001"
    acestep_api_key: str = ""

    # ACE-Step model defaults
    acestep_config_path: str = "acestep-v15-turbo"
    acestep_lm_model_path: str = "acestep-5Hz-lm-1.7B"

    # Output
    output_dir: Path = Path("outputs")

    # Generation defaults
    default_duration: int = 120
    default_format: str = "mp3"
    default_model: str = "turbo"
    default_batch_size: int = 1

    # Polling
    poll_interval: float = 2.0
    poll_timeout: float = 300.0

    # Web UI
    web_host: str = "127.0.0.1"
    web_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///data/ace_music.db"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Load settings from environment/.env file."""
    return Settings()
