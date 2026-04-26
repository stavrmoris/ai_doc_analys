from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.core.config import settings
from app.domain.retrieval import RetrievedChunk
from app.schemas.qa import Citation, QAResponse
from app.services.openrouter import OpenRouterChatClient
from app.services.retrieval import RetrievalService
from app.services.text_normalization import tokenize_text


REFUSAL_ANSWER = "I could not find enough evidence in the document."


class RetrievalForQA(Protocol):
    def retrieve_for_qa(
        self,
        question: str,
        doc_id: int | None = None,
        top_k: int = 20,
    ) -> list[RetrievedChunk]:
        ...


class Reranker(Protocol):
    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        ...


class GroundedAnswerClient(Protocol):
    def answer_question(self, question: str, chunks: list[RetrievedChunk]) -> "GroundedAnswerResult | None":
        ...


@dataclass(slots=True)
class GroundedAnswerResult:
    answer: str
    supporting_chunks: list[RetrievedChunk]


class RetrievalQAAdapter:
    def __init__(self, retrieval_service: RetrievalService) -> None:
        self.retrieval_service = retrieval_service

    def retrieve_for_qa(
        self,
        question: str,
        doc_id: int | None = None,
        top_k: int = 20,
    ) -> list[RetrievedChunk]:
        results = self.retrieval_service.search(query=question, limit=top_k, doc_id=doc_id)
        chunks: list[RetrievedChunk] = []
        for index, item in enumerate(results):
            chunks.append(
                RetrievedChunk(
                    chunk_id=f"{item.doc_id}:{item.page_num}:{index}",
                    doc_id=item.doc_id,
                    page_num=item.page_num,
                    section_title=item.section_title,
                    text=item.text,
                    retrieval_score=item.score,
                )
            )
        return chunks


class PromptedGroundedAnswerClient:
    def __init__(
        self,
        prompt_path: Path | None = None,
        openrouter_client: OpenRouterChatClient | None = None,
    ) -> None:
        self.prompt_path = prompt_path or Path(__file__).resolve().parent.parent / "prompts" / "qa_prompt.txt"
        self._prompt_template: str | None = None
        self.openrouter_client = openrouter_client

    def answer_question(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswerResult | None:
        if not chunks:
            return None

        prompt = self._render_prompt(question=question, chunks=chunks)
        llm_answer = None
        if self.openrouter_client is not None:
            llm_answer = self.openrouter_client.complete(
                system_prompt=(
                    "Answer questions using only the provided document evidence. "
                    "If the context is insufficient, return an empty response. "
                    "Keep the answer concise and in the same language as the question."
                ),
                user_prompt=prompt,
                temperature=0.0,
                max_tokens=220,
            )
        if llm_answer:
            return GroundedAnswerResult(
                answer=llm_answer,
                supporting_chunks=self._select_supporting_chunks(
                    question=question,
                    answer=llm_answer,
                    chunks=chunks,
                ),
            )

        best_match = self._best_supported_sentence(question=question, chunks=chunks)
        if best_match is None:
            return None

        return GroundedAnswerResult(
            answer=best_match["sentence"],
            supporting_chunks=[best_match["chunk"]],
        )

    def _render_prompt(self, question: str, chunks: list[RetrievedChunk]) -> str:
        if self._prompt_template is None:
            self._prompt_template = self.prompt_path.read_text(encoding="utf-8").strip()

        context_lines = []
        for chunk in chunks:
            page_label = "unknown" if chunk.page_num is None else str(chunk.page_num)
            context_lines.append(f"[doc:{chunk.doc_id} page:{page_label}] {chunk.text}")

        return self._prompt_template.format(question=question, context="\n".join(context_lines))

    @staticmethod
    def _select_supporting_chunks(
        question: str,
        answer: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        question_terms = tokenize_text(question)
        answer_terms = tokenize_text(answer)
        focus_terms = answer_terms or question_terms
        if not focus_terms:
            return chunks[:1]

        ranked = sorted(
            chunks,
            key=lambda chunk: (
                len(focus_terms & tokenize_text(chunk.text)),
                len(question_terms & tokenize_text(chunk.text)),
                chunk.rerank_score or chunk.retrieval_score,
            ),
            reverse=True,
        )
        selected: list[RetrievedChunk] = []
        for chunk in ranked:
            chunk_terms = tokenize_text(chunk.text)
            overlap = len(focus_terms & chunk_terms)
            if overlap == 0:
                continue
            selected.append(chunk)
            break

        return selected or ranked[:1]

    @staticmethod
    def _best_supported_sentence(question: str, chunks: list[RetrievedChunk]) -> dict | None:
        query_terms = tokenize_text(question)
        if not query_terms:
            return None

        best_match: dict | None = None
        best_score = 0.0

        for chunk in chunks:
            for sentence in PromptedGroundedAnswerClient._split_sentences(chunk.text):
                sentence_terms = tokenize_text(sentence)
                overlap = query_terms & sentence_terms
                overlap_count = len(overlap)
                if overlap_count < 2:
                    continue

                score = overlap_count / len(query_terms)
                if score > best_score:
                    best_match = {
                        "sentence": sentence,
                        "chunk": chunk,
                        "score": score,
                    }
                    best_score = score

        if best_match is None or best_score < 0.4:
            return None

        return best_match

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        normalized = text.replace("\n", " ")
        parts = [part.strip() for part in normalized.split(".")]
        return [f"{part}." for part in parts if part]


class QAService:
    def __init__(
        self,
        retrieval_service: RetrievalForQA,
        reranker_service: Reranker,
        llm_client: GroundedAnswerClient,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.reranker_service = reranker_service
        self.llm_client = llm_client

    def answer(self, question: str, doc_id: int | None = None) -> QAResponse:
        retrieved = self.retrieval_service.retrieve_for_qa(
            question=question,
            doc_id=doc_id,
            top_k=settings.retrieval_top_k,
        )
        reranked = self.reranker_service.rerank(question, retrieved, top_k=settings.answer_top_k)
        if not reranked:
            return QAResponse(answer=REFUSAL_ANSWER, citations=[])

        grounded_answer = self.llm_client.answer_question(question=question, chunks=reranked)
        if grounded_answer is None or not grounded_answer.answer.strip():
            return QAResponse(answer=REFUSAL_ANSWER, citations=[])

        citations = [
            Citation(doc_id=item.doc_id, page=item.page_num, text=item.text)
            for item in grounded_answer.supporting_chunks
        ]
        return QAResponse(answer=grounded_answer.answer.strip(), citations=citations)


__all__ = [
    "GroundedAnswerClient",
    "GroundedAnswerResult",
    "PromptedGroundedAnswerClient",
    "QAService",
    "REFUSAL_ANSWER",
    "RetrievalForQA",
    "RetrievalQAAdapter",
    "Reranker",
]
