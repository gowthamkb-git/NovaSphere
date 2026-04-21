from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        salt, stored_digest = hashed_password.split("$", maxsplit=1)
    except ValueError:
        return False

    computed_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hmac.compare_digest(computed_digest, stored_digest)


def create_access_token(*, subject: str, email: str) -> str:
    settings = get_settings()
    expire_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "email": email,
        "exp": expire_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        ) from exc
