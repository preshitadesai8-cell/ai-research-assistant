"""Load and validate application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Runtime settings required by the application."""

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"


def load_settings() -> Settings:
    """Load settings from the process environment or supported dotenv files.

    Existing process environment variables take precedence over values in
    either dotenv file.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(Path(__file__).resolve().parent / ".env")

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is not configured. Set it in the environment or "
            "in .env / config/.env (see config/.env.example)."
        )

    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
    if not model:
        raise ValueError("GROQ_MODEL cannot be empty.")

    return Settings(groq_api_key=api_key, groq_model=model)
