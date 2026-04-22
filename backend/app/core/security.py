from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta


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


def create_session_token() -> str:
    return secrets.token_urlsafe(48)


def get_session_expiry(*, days: int) -> datetime:
    return datetime.now(UTC) + timedelta(days=days)
