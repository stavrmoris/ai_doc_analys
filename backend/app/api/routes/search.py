from fastapi import APIRouter
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.retrieval import RetrievalService


router = APIRouter(prefix="/search", tags=["search"])


def build_retrieval_service() -> RetrievalService:
    return RetrievalService()


@router.post("", response_model=SearchResponse)
def search_documents(payload: SearchRequest) -> SearchResponse:
    retrieval = build_retrieval_service()
    results = retrieval.search(query=payload.query, limit=payload.limit, doc_id=payload.doc_id)
    return SearchResponse(results=[SearchResult.model_validate(result) for result in results])
