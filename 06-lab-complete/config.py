"""Minimal config for the MVP Streamlit app."""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env.local")
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", os.getenv("LLM_MODEL", "gpt-4o-mini")))
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "DevCoach MVP"))
    max_upload_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "5")))


settings = Settings()
