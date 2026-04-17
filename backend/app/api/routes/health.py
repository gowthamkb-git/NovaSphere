from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": "Company Knowledge Assistant API is running"}


@router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
