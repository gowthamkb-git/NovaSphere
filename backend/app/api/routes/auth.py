from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongo import get_users_collection
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


def _build_auth_response(user_document: dict) -> AuthResponse:
    user = _serialize_user(user_document)
    return AuthResponse(
        access_token=create_access_token(subject=user.id, email=user.email),
        user=user,
    )


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignupRequest) -> AuthResponse:
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
    return _build_auth_response(inserted)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
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
    return _build_auth_response(user_document)


@router.get("/me", response_model=AuthUser)
def get_me(current_user: dict = Depends(get_current_user)) -> AuthUser:
    return _serialize_user(current_user)
