"""Configuration for AI Execution Agent backend."""

import os
from typing import Optional


class Settings:
    """Application settings."""

    def __init__(self):
        # LLM Configuration
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-4")

        # Backend Configuration
        self.backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
        self.backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))

        # Calendar Configuration
        self.calendar_id: str = os.getenv("CALENDAR_ID", "primary")

        # Security Configuration
        self.cors_origins: list = os.getenv("CORS_ORIGINS", "chrome-extension://*").split(",")


settings = Settings()
