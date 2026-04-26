from fastapi import APIRouter

from app.core.config import settings
from app.core.database import SessionLocal
from app.db.models import Chunk
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.openrouter import OpenRouterChatClient
from app.services.summary import PromptedSummaryClient, SummaryService


router = APIRouter(tags=["summary"])


def build_summary_service() -> SummaryService:
    return SummaryService(
        llm_client=PromptedSummaryClient(
            openrouter_client=OpenRouterChatClient(
                api_key=settings.openrouter_api_key,
                model=settings.openrouter_model,
            )
        )
    )


def load_document_chunks(doc_id: int) -> list[str]:
    db = SessionLocal()
    try:
        rows = (
            db.query(Chunk.text)
            .filter(Chunk.doc_id == doc_id)
            .order_by(Chunk.chunk_index.asc())
            .all()
        )
    finally:
        db.close()

    return [row[0] for row in rows]


@router.post("/summary", response_model=SummaryResponse)
def summarize_document(payload: SummaryRequest) -> SummaryResponse:
    summary_service = build_summary_service()
    summary = summary_service.summarize(
        chunks=load_document_chunks(payload.doc_id),
        mode=payload.mode,
    )
    return SummaryResponse(summary=summary)
