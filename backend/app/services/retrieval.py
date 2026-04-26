from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.db.models import Chunk
from app.services.embeddings import EmbeddingClient, build_default_embedding_client
from app.services.text_normalization import tokenize_text, weighted_overlap_score
from app.services.vector_store import VectorStore, build_default_vector_store


class RetrievalResult(BaseModel):
    doc_id: int
    page_num: int | None = None
    section_title: str | None = None
    text: str
    score: float


class RetrievalService:
    def __init__(
        self,
        embedding_client: EmbeddingClient | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embedding_client = embedding_client or build_default_embedding_client()
        self.vector_store = vector_store or build_default_vector_store()

    def search(self, query: str, limit: int, doc_id: int | None = None) -> list[RetrievalResult]:
        query_vector = self.embedding_client.embed_texts([query])[0]
        filters = {"doc_id": doc_id} if doc_id is not None else None
        raw_results = self.vector_store.search(query_vector=query_vector, limit=limit, filters=filters)
        vector_results = [self._to_result(item) for item in raw_results]
        lexical_results = self._lexical_search(query=query, limit=max(limit, 10), doc_id=doc_id)
        return self._merge_results(vector_results + lexical_results)[:limit]

    @staticmethod
    def _to_result(item: object) -> RetrievalResult:
        payload = getattr(item, "payload", None)
        if payload is None and isinstance(item, dict):
            payload = item.get("payload", {})

        score = getattr(item, "score", None)
        if score is None and isinstance(item, dict):
            score = item.get("score", 0.0)

        if payload is None:
            payload = {}

        return RetrievalResult(
            doc_id=int(payload["doc_id"]),
            page_num=payload.get("page_num"),
            section_title=payload.get("section_title"),
            text=payload.get("text", ""),
            score=float(score or 0.0),
        )

    @staticmethod
    def _lexical_search(query: str, limit: int, doc_id: int | None) -> list[RetrievalResult]:
        query_terms = tokenize_text(query)
        if not query_terms:
            return []

        db = SessionLocal()
        try:
            rows_query = db.query(Chunk)
            if doc_id is not None:
                rows_query = rows_query.filter(Chunk.doc_id == doc_id)
            chunks = rows_query.all()
        except SQLAlchemyError:
            chunks = []
        finally:
            db.close()

        results: list[RetrievalResult] = []
        for chunk in chunks:
            chunk_terms = tokenize_text(chunk.text)
            overlap = query_terms & chunk_terms
            if not overlap:
                continue

            score = weighted_overlap_score(query_terms, chunk_terms)
            score += len(overlap) / max(len(chunk_terms), 1)
            results.append(
                RetrievalResult(
                    doc_id=chunk.doc_id,
                    page_num=chunk.page_num,
                    section_title=chunk.section_title,
                    text=chunk.text,
                    score=score,
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    @staticmethod
    def _merge_results(results: list[RetrievalResult]) -> list[RetrievalResult]:
        merged: dict[tuple[int, int | None, str], RetrievalResult] = {}
        for result in results:
            key = (result.doc_id, result.page_num, result.text)
            existing = merged.get(key)
            if existing is None or result.score > existing.score:
                merged[key] = result
        return sorted(merged.values(), key=lambda item: item.score, reverse=True)
