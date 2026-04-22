from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.dependencies.auth import get_current_user
from app.core.config import get_settings
from app.core.security import (
    create_session_token,
    get_session_expiry,
    hash_password,
    verify_password,
)
from app.db.mongo import get_sessions_collection, get_users_collection
from app.schemas.auth import AuthResponse, AuthUser, LoginRequest, SignupRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _serialize_user(document: dict) -> AuthUser:
    return AuthUser(
        id=str(document["_id"]),
        full_name=document["full_name"],
        email=document["email"],
        created_at=(document.get("created_at") or _utc_now()).isoformat(),
    )


def _set_session_cookie(response: Response, *, session_id: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.session_expire_days * 24 * 60 * 60,
        path="/",
    )


def _create_session(*, user_document: dict) -> str:
    session_id = create_session_token()
    now = _utc_now()
    get_sessions_collection().insert_one(
        {
            "session_id": session_id,
            "user_id": str(user_document["_id"]),
            "created_at": now,
            "expires_at": get_session_expiry(days=get_settings().session_expire_days),
        }
    )
    return session_id


def _build_auth_response(user_document: dict) -> AuthResponse:
    user = _serialize_user(user_document)
    return AuthResponse(user=user)


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, response: Response) -> AuthResponse:
    users = get_users_collection()
    normalized_email = payload.email.strip().lower()

    existing_user = users.find_one({"email": normalized_email}, {"_id": 1})
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    now = _utc_now()
    inserted = {
        "full_name": " ".join(payload.full_name.split()).strip(),
        "email": normalized_email,
        "password_hash": hash_password(payload.password),
        "created_at": now,
        "updated_at": now,
        "last_login_at": now,
    }
    result = users.insert_one(inserted)
    inserted["_id"] = result.inserted_id
    _set_session_cookie(response, session_id=_create_session(user_document=inserted))
    return _build_auth_response(inserted)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response) -> AuthResponse:
    users = get_users_collection()
    normalized_email = payload.email.strip().lower()
    user_document = users.find_one({"email": normalized_email})
    if user_document is None or not verify_password(
        payload.password, user_document.get("password_hash", "")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    now = _utc_now()
    users.update_one(
        {"_id": user_document["_id"]},
        {"$set": {"last_login_at": now, "updated_at": now}},
    )
    user_document["last_login_at"] = now
    user_document["updated_at"] = now
    _set_session_cookie(response, session_id=_create_session(user_document=user_document))
    return _build_auth_response(user_document)


@router.get("/me", response_model=AuthUser)
def get_me(current_user: dict = Depends(get_current_user)) -> AuthUser:
    return _serialize_user(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
) -> Response:
    del current_user
    settings = get_settings()
    session_cookie = settings.session_cookie_name
    session_id = request.cookies.get(session_cookie)
    if session_id:
        get_sessions_collection().delete_one({"session_id": session_id})
    response.delete_cookie(key=session_cookie, path="/")
    return response
