from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from rag.retrieval.vector_search import validate_vector_search_index

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def validate_rag_dependencies() -> None:
    if not settings.mongodb_uri.strip():
        raise RuntimeError("MONGODB_URI is not set.")
    if not settings.groq_api_key.strip():
        raise RuntimeError("GROQ_API_KEY is not set.")
    validate_vector_search_index()
