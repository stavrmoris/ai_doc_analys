from fastapi import APIRouter

from app.core.config import settings
from app.services.openrouter import OpenRouterChatClient
from app.schemas.qa import QARequest, QAResponse
from app.services.qa import PromptedGroundedAnswerClient, QAService, RetrievalQAAdapter
from app.services.reranking import RerankerService
from app.services.retrieval import RetrievalService


router = APIRouter(tags=["qa"])


def build_qa_service() -> QAService:
    retrieval = RetrievalQAAdapter(RetrievalService())
    reranker = RerankerService()
    llm_client = PromptedGroundedAnswerClient(
        openrouter_client=OpenRouterChatClient(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
        )
    )
    return QAService(
        retrieval_service=retrieval,
        reranker_service=reranker,
        llm_client=llm_client,
    )


@router.post("/qa", response_model=QAResponse)
def answer_question(payload: QARequest) -> QAResponse:
    qa_service = build_qa_service()
    return qa_service.answer(question=payload.question, doc_id=payload.doc_id)
