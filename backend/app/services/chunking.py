from __future__ import annotations

from app.core.config import settings
from app.domain.chunks import ChunkRecord, ChunkingConfig
from app.domain.documents import DocumentBlock, StructuredDocument


class ChunkingService:
    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        if self.config.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.config.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if self.config.chunk_overlap >= self.config.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

    def chunk_document(self, document: StructuredDocument) -> list[ChunkRecord]:
        chunks: list[ChunkRecord] = []
        chunk_index = 0

        for page in document.pages:
            for block in page.blocks:
                chunk_index = self._chunk_block(
                    document_id=document.doc_id,
                    page_num=page.page_num,
                    block=block,
                    chunk_index=chunk_index,
                    chunks=chunks,
                )

        return chunks

    def _chunk_block(
        self,
        *,
        document_id: str,
        page_num: int,
        block: DocumentBlock,
        chunk_index: int,
        chunks: list[ChunkRecord],
    ) -> int:
        text = block.text
        if not text.strip():
            return chunk_index

        step = self.config.chunk_size - self.config.chunk_overlap
        start = 0

        while start < len(text):
            end = min(start + self.config.chunk_size, len(text))
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(
                    ChunkRecord(
                        chunk_id=f"{document_id}:{page_num}:{chunk_index}",
                        doc_id=document_id,
                        page_num=page_num,
                        chunk_index=chunk_index,
                        section_title=block.section_title,
                        text=chunk_text,
                        metadata={
                            "doc_id": document_id,
                            "page_num": str(page_num),
                            "chunk_index": str(chunk_index),
                            "section_title": block.section_title,
                        },
                    )
                )
                chunk_index += 1

            if end >= len(text):
                break

            start += step

        return chunk_index
