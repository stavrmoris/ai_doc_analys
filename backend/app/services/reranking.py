from __future__ import annotations

from app.domain.retrieval import RetrievedChunk
from app.services.text_normalization import tokenize_text, weighted_overlap_score


class RerankerService:
    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        query_terms = tokenize_text(query)
        ranked = sorted(
            candidates,
            key=lambda item: self._score(query_terms=query_terms, candidate=item),
            reverse=True,
        )
        reranked: list[RetrievedChunk] = []
        for index, item in enumerate(ranked[:top_k]):
            rerank_score = self._score(query_terms=query_terms, candidate=item)
            reranked.append(
                RetrievedChunk(
                    chunk_id=item.chunk_id,
                    doc_id=item.doc_id,
                    page_num=item.page_num,
                    section_title=item.section_title,
                    text=item.text,
                    retrieval_score=item.retrieval_score,
                    rerank_score=rerank_score,
                )
            )
        return reranked

    @staticmethod
    def _score(query_terms: set[str], candidate: RetrievedChunk) -> float:
        if not query_terms:
            return candidate.retrieval_score

        candidate_terms = tokenize_text(candidate.text)
        if not candidate_terms:
            return candidate.retrieval_score

        overlap = query_terms & candidate_terms
        lexical_score = weighted_overlap_score(query_terms, candidate_terms)
        density_bonus = len(overlap) / max(len(candidate_terms), 1)
        return candidate.retrieval_score + lexical_score + density_bonus
