import logging
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_chat_history_collection
from app.schemas.assistant import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
)
from rag.agents.router import route_query

logger = logging.getLogger(__name__)

router = APIRouter()


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _format_timestamp(value: datetime | None) -> str:
    return (value or _utc_now()).isoformat()


def _build_title(question: str) -> str:
    cleaned_question = " ".join(question.split()).strip()
    if len(cleaned_question) <= 48:
        return cleaned_question
    return f"{cleaned_question[:45].rstrip()}..."


def _serialize_message(message: dict) -> ChatMessage:
    return ChatMessage(
        role=message.get("role", "assistant"),
        content=message.get("content", ""),
        sources=message.get("sources") or [],
        created_at=_format_timestamp(message.get("created_at")),
    )


def _serialize_summary(document: dict) -> ConversationSummary:
    messages = document.get("messages") or []
    preview = next(
        (message.get("content", "") for message in reversed(messages) if message.get("content")),
        "",
    )
    return ConversationSummary(
        conversation_id=document["conversation_id"],
        title=document.get("title", "Untitled chat"),
        preview=preview[:120],
        updated_at=_format_timestamp(document.get("updated_at")),
        message_count=len(messages),
    )


def _get_conversation_or_404(*, session_id: str, conversation_id: str) -> dict:
    document = get_chat_history_collection().find_one(
        {"session_id": session_id, "conversation_id": conversation_id},
        {"_id": 0},
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return document


@router.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat(payload: ChatRequest) -> ChatResponse:
    session_id = payload.session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    collection = get_chat_history_collection()
    conversation_id = payload.conversation_id.strip() if payload.conversation_id else str(uuid4())
    now = _utc_now()

    existing_conversation = collection.find_one(
        {"session_id": session_id, "conversation_id": conversation_id},
        {"_id": 0, "conversation_id": 1},
    )
    if existing_conversation is None:
        collection.insert_one(
            {
                "conversation_id": conversation_id,
                "session_id": session_id,
                "title": _build_title(payload.question),
                "created_at": now,
                "updated_at": now,
                "messages": [],
            }
        )

    try:
        result = route_query(payload.question, department=payload.department)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError:
        logger.exception("Chat request failed due to backend configuration")
        raise HTTPException(status_code=500, detail="Chat backend is not configured correctly.") from None
    except Exception:
        logger.exception("Unexpected error during chat request")
        raise HTTPException(status_code=500, detail="Failed to generate answer.") from None

    assistant_created_at = _utc_now()
    collection.update_one(
        {"session_id": session_id, "conversation_id": conversation_id},
        {
            "$push": {
                "messages": {
                    "$each": [
                        {
                            "role": "user",
                            "content": payload.question,
                            "sources": [],
                            "created_at": now,
                        },
                        {
                            "role": "assistant",
                            "content": result["answer"],
                            "sources": result["sources"],
                            "created_at": assistant_created_at,
                        },
                    ]
                }
            },
            "$set": {"updated_at": assistant_created_at},
        },
    )

    return ChatResponse(
        conversation_id=conversation_id,
        answer=result["answer"],
        sources=result["sources"],
    )


@router.get("/chat/history", response_model=list[ConversationSummary], tags=["chat"])
def get_chat_history(session_id: str = Query(..., min_length=1)) -> list[ConversationSummary]:
    documents = list(
        get_chat_history_collection()
        .find({"session_id": session_id.strip()}, {"_id": 0})
        .sort("updated_at", -1)
    )
    return [_serialize_summary(document) for document in documents]


@router.get("/chat/history/{conversation_id}", response_model=ConversationDetail, tags=["chat"])
def get_chat_conversation(
    conversation_id: str,
    session_id: str = Query(..., min_length=1),
) -> ConversationDetail:
    document = _get_conversation_or_404(
        session_id=session_id.strip(),
        conversation_id=conversation_id,
    )
    return ConversationDetail(
        conversation_id=document["conversation_id"],
        title=document.get("title", "Untitled chat"),
        updated_at=_format_timestamp(document.get("updated_at")),
        messages=[_serialize_message(message) for message in document.get("messages", [])],
    )
