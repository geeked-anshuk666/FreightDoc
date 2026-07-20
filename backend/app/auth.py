"""Clerk JWT verification and owner identity extraction.

Only the verified ``sub`` claim is exposed to application code.  Callers cannot
supply an owner ID in a body/header and authentication is deliberately disabled
with a clear error—not a development bypass—when Clerk verifier settings are
missing.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
import fastapi.security as fastapi_security
from fastapi.security import HTTPAuthorizationCredentials

from app.config import Settings, get_settings

_bearer = fastapi_security.HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    owner_id: str


class ClerkJwksCache:
    def __init__(self) -> None:
        self._keys: dict[str, dict] = {}
        self._expires_at = 0.0
        self._lock = asyncio.Lock()

    async def _refresh(self, settings: Settings) -> None:
        assert settings.clerk_jwks_url
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
            response = await client.get(settings.clerk_jwks_url)
            response.raise_for_status()
        payload = response.json()
        keys = payload.get("keys")
        if not isinstance(keys, list):
            raise ValueError("JWKS response has no keys")
        indexed = {str(key.get("kid")): key for key in keys if isinstance(key, dict) and key.get("kid")}
        if not indexed:
            raise ValueError("JWKS response has no usable key IDs")
        self._keys = indexed
        self._expires_at = time.monotonic() + max(60, settings.clerk_jwks_cache_seconds)

    async def key_for(self, kid: str, settings: Settings):
        async with self._lock:
            if time.monotonic() >= self._expires_at or kid not in self._keys:
                await self._refresh(settings)
            jwk = self._keys.get(kid)
            if jwk is None:
                # Key rotations can race a cache refresh; one retry gives Clerk
                # the chance to publish the newly issued key without accepting it.
                await self._refresh(settings)
                jwk = self._keys.get(kid)
        if jwk is None:
            raise KeyError("Unknown signing key")
        return jwt.PyJWK.from_dict(jwk).key


_jwks_cache = ClerkJwksCache()


def _auth_error(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


async def require_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    settings = get_settings()
    if not settings.clerk_auth_configured:
        raise _auth_error(
            "AUTH_NOT_CONFIGURED",
            "Workspace authentication is not configured on this API. Configure Clerk issuer and JWKS settings.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _auth_error("AUTH_REQUIRED", "A valid Clerk authorization credential is required.", status.HTTP_401_UNAUTHORIZED)

    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        algorithm = header.get("alg")
        if not isinstance(kid, str) or algorithm not in settings.clerk_jwt_algorithms:
            raise jwt.InvalidTokenError("Unsupported token header")
        key = await _jwks_cache.key_for(kid, settings)
        decode_kwargs: dict = {
            "algorithms": list(settings.clerk_jwt_algorithms),
            "issuer": settings.clerk_issuer,
            "options": {"require": ["exp", "iat", "sub"], "verify_aud": bool(settings.clerk_audience)},
        }
        if settings.clerk_audience:
            decode_kwargs["audience"] = settings.clerk_audience
        claims = jwt.decode(token, key, **decode_kwargs)
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject or len(subject) > 128:
            raise jwt.InvalidTokenError("Invalid subject")
        # Request state is for audit correlation only; no token or profile data.
        request.state.owner_id = subject
        return CurrentUser(owner_id=subject)
    except (jwt.PyJWTError, httpx.HTTPError, ValueError, KeyError):
        raise _auth_error("AUTH_INVALID", "The Clerk access token could not be verified.", status.HTTP_401_UNAUTHORIZED)
