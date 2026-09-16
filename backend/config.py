"""
Author: Mourad.Soltani
Config loader for ResolveFabric P2P
"""

import os
from typing import Optional

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

class Config:
    AUTHOR = "Mourad.Soltani"
    VERSION = "3.0.0"
    PROJECT = "resolvefabric-p2p"
    SIGNATURE = "Mourad.Soltani"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8080"))
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024)))  # 5MB, >=1MB requirement

    # AI Layer
    AI_REQUIRED = os.getenv("AI_REQUIRED", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "12"))
    AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "2"))
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "800"))
    AI_COST_GUARD_CENTS = int(os.getenv("AI_COST_GUARD_CENTS", "10"))  # max 10 cents per call estimate

    # Integrations
    SAP_MOCK_ENABLED = os.getenv("SAP_MOCK_ENABLED", "true").lower() == "true"
    NETSUITE_MOCK_ENABLED = os.getenv("NETSUITE_MOCK_ENABLED", "true").lower() == "true"

    # Data pipeline
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///resolvefabric.db")
    REDIS_URL = os.getenv("REDIS_URL", "")

    @classmethod
    def validate(cls):
        errors = []
        if cls.AI_REQUIRED and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when AI_REQUIRED=true")
        if cls.MAX_CONTENT_LENGTH < 1 * 1024 * 1024:
            errors.append("MAX_CONTENT_LENGTH must be >=1MB per enterprise payload requirement")
        return errors

    @classmethod
    def ai_configured(cls) -> bool:
        return bool(cls.OPENAI_API_KEY)

config = Config()
