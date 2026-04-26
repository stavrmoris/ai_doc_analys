from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.services.chunking import ChunkingService
from app.services.embeddings import EmbeddingClient, build_default_embedding_client
from app.services.parsers.pdf_parser import PdfParser
from app.services.parsers.txt_parser import TxtParser
from app.services.vector_store import VectorStore, build_default_vector_store


class IngestionService:
    def __init__(
        self,
        chunking_service: ChunkingService | None = None,
        embedding_client: EmbeddingClient | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_client = embedding_client or build_default_embedding_client()
        self.vector_store = vector_store or build_default_vector_store()

    def ingest_document(self, db: Session, document: Document) -> Document:
        parser = self._get_parser(document.file_type)
        structured = parser.parse(Path(document.storage_path))
        structured.doc_id = str(document.id)

        chunks = self.chunking_service.chunk_document(structured)

        document.chunks.clear()
        db.flush()

        indexed_chunks: list[dict] = []
        for chunk in chunks:
            db_chunk = Chunk(
                doc_id=document.id,
                page_num=chunk.page_num,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                section_title=chunk.section_title,
                metadata_json=json.dumps(chunk.metadata),
            )
            db.add(db_chunk)
            indexed_chunks.append(
                {
                    "id": chunk.chunk_id,
                    "text": chunk.text,
                    "page_num": chunk.page_num,
                    "section_title": chunk.section_title,
                }
            )

        if indexed_chunks:
            vectors = self.embedding_client.embed_texts([item["text"] for item in indexed_chunks])
            self.vector_store.upsert_chunks(
                [
                    {
                        "id": item["id"],
                        "vector": vector,
                        "payload": {
                            "doc_id": document.id,
                            "page_num": item["page_num"],
                            "section_title": item["section_title"],
                            "text": item["text"],
                        },
                    }
                    for item, vector in zip(indexed_chunks, vectors, strict=True)
                ]
            )

        document.pages_count = len(structured.pages)
        document.status = "ready"
        document.error_message = None
        db.add(document)
        db.flush()
        return document

    @staticmethod
    def _get_parser(file_type: str):
        normalized_type = file_type.lower()
        if normalized_type == "txt":
            return TxtParser()
        if normalized_type == "pdf":
            return PdfParser()
        raise ValueError(f"Unsupported file type: {file_type}")
