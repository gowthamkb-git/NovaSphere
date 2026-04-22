from bson import ObjectId
from bson.errors import InvalidId
from datetime import UTC, datetime
from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.db.mongo import get_sessions_collection, get_users_collection


def _as_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def get_current_user(request: Request) -> dict:
    session_cookie_name = get_settings().session_cookie_name
    novasphere_session = request.cookies.get(session_cookie_name)
    if not novasphere_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    session = get_sessions_collection().find_one({"session_id": novasphere_session})
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        )

    expires_at = _as_utc_datetime(session.get("expires_at"))
    if expires_at is None or expires_at <= datetime.now(UTC):
        get_sessions_collection().delete_one({"session_id": novasphere_session})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired.",
        )

    user_id = session.get("user_id")

    try:
        object_id = ObjectId(user_id)
    except InvalidId as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session.",
        ) from exc

    user = get_users_collection().find_one({"_id": object_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user
