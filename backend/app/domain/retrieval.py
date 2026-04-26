from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    doc_id: int
    page_num: int | None
    section_title: str | None
    text: str
    retrieval_score: float
    rerank_score: float | None = None
