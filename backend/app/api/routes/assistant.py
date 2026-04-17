import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.schemas.assistant import AskQuestionRequest, AskQuestionResponse
from app.schemas.knowledge_base import IngestionResponse
from app.services.company_knowledge_service import answer_company_question
from app.services.document_ingestion_service import ingest_seed_knowledge

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=AskQuestionResponse)
def ask_question(payload: AskQuestionRequest) -> AskQuestionResponse:
    try:
        answer = answer_company_question(payload.question, department=payload.department)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError:
        logger.exception("Assistant request failed due to backend configuration")
        raise HTTPException(status_code=500, detail="Assistant backend is not configured correctly.") from None
    except Exception:
        logger.exception("Unexpected error during assistant request")
        raise HTTPException(status_code=500, detail="Failed to answer question.") from None
    return AskQuestionResponse(answer=answer)


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_documents() -> IngestionResponse:
    logger.info("Starting knowledge-base ingestion request")
    inserted_documents = await run_in_threadpool(ingest_seed_knowledge)
    return IngestionResponse(
        status="Knowledge base ingested successfully",
        inserted_documents=inserted_documents,
    )
