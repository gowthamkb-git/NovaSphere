from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Header, HTTPException, status

from app.core.security import decode_access_token
from app.db.mongo import get_users_collection


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    token = authorization.split(" ", maxsplit=1)[1].strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    try:
        object_id = ObjectId(user_id)
    except InvalidId as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        ) from exc

    user = get_users_collection().find_one({"_id": object_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user
