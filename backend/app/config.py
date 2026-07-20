"""Runtime configuration for FreightDoc.

Secrets are deliberately read only from the process environment.  In particular,
Clerk profile data and credentials must never be accepted from frontend requests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None
    ai_provider: str
    ai_model: str
    allowed_origins: str
    request_timeout_seconds: float
    document_parser_timeout_seconds: float
    low_confidence_threshold: float
    database_url: str | None
    clerk_jwks_url: str | None
    clerk_issuer: str | None
    clerk_audience: str | None
    clerk_jwt_algorithms: tuple[str, ...]
    clerk_jwks_cache_seconds: int
    rate_limit_window_seconds: int

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def clerk_auth_configured(self) -> bool:
        """True only when the API can verify an incoming Clerk token safely."""
        return bool(self.clerk_jwks_url and self.clerk_issuer)


@lru_cache
def get_settings() -> Settings:
    load_dotenv(override=True)
    algorithms = tuple(
        algorithm.strip() for algorithm in os.getenv("CLERK_JWT_ALGORITHMS", "RS256").split(",") if algorithm.strip()
    )
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        # The code currently uses Groq.  These settings make that fact auditable
        # instead of claiming an unavailable model provider.
        ai_provider=os.getenv("AI_PROVIDER", "groq"),
        ai_model=os.getenv("AI_MODEL", "llama-3.3-70b-versatile"),
        allowed_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173"),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "8")),
        document_parser_timeout_seconds=float(os.getenv("DOCUMENT_PARSER_TIMEOUT_SECONDS", "12")),
        low_confidence_threshold=float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.75")),
        database_url=os.getenv("DATABASE_URL"),
        clerk_jwks_url=os.getenv("CLERK_JWKS_URL"),
        clerk_issuer=os.getenv("CLERK_ISSUER") or os.getenv("CLERK_JWT_ISSUER"),
        clerk_audience=os.getenv("CLERK_AUDIENCE") or os.getenv("CLERK_JWT_AUDIENCE"),
        clerk_jwt_algorithms=algorithms or ("RS256",),
        clerk_jwks_cache_seconds=int(os.getenv("CLERK_JWKS_CACHE_SECONDS", "3600")),
        rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
    )
