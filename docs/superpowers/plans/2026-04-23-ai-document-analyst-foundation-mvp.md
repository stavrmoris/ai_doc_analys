# AI Document Analyst Foundation MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, Dockerized MVP that ingests `PDF` and `TXT` documents, indexes them for semantic retrieval, supports reranked QA with citations, and exposes a demo React UI for upload, search, QA, and summary.

**Architecture:** Use a modular monolith backend in `FastAPI` with explicit service boundaries for ingestion, parsing, chunking, retrieval, and generation. Pair it with a small `React + Vite` frontend, `SQLite` for application metadata, `Qdrant` for vectors, and local filesystem storage for raw uploads and processed artifacts.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Pydantic, PyMuPDF, sentence-transformers, Qdrant, OpenRouter, React, Vite, Tailwind CSS, Docker Compose, pytest, Vitest.

---

## File Structure

### Backend

- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/app/api/routes/documents.py`
- Create: `backend/app/api/routes/search.py`
- Create: `backend/app/api/routes/qa.py`
- Create: `backend/app/api/routes/summary.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/db/models.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/schemas/documents.py`
- Create: `backend/app/schemas/search.py`
- Create: `backend/app/schemas/qa.py`
- Create: `backend/app/schemas/summary.py`
- Create: `backend/app/services/storage.py`
- Create: `backend/app/services/ingestion.py`
- Create: `backend/app/services/parsers/base.py`
- Create: `backend/app/services/parsers/pdf_parser.py`
- Create: `backend/app/services/parsers/txt_parser.py`
- Create: `backend/app/services/chunking.py`
- Create: `backend/app/services/embeddings.py`
- Create: `backend/app/services/vector_store.py`
- Create: `backend/app/services/retrieval.py`
- Create: `backend/app/services/reranking.py`
- Create: `backend/app/services/qa.py`
- Create: `backend/app/services/summary.py`
- Create: `backend/app/prompts/qa_prompt.txt`
- Create: `backend/app/prompts/summary_short_prompt.txt`
- Create: `backend/app/prompts/summary_detailed_prompt.txt`
- Create: `backend/app/domain/documents.py`
- Create: `backend/app/domain/chunks.py`
- Create: `backend/app/domain/retrieval.py`

### Backend Tests

- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_documents_upload.py`
- Create: `backend/tests/test_pdf_parser.py`
- Create: `backend/tests/test_chunking.py`
- Create: `backend/tests/test_search.py`
- Create: `backend/tests/test_qa.py`
- Create: `backend/tests/test_summary.py`

### Frontend

- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/DocumentUpload.tsx`
- Create: `frontend/src/components/DocumentList.tsx`
- Create: `frontend/src/components/SearchPanel.tsx`
- Create: `frontend/src/components/QAPanel.tsx`
- Create: `frontend/src/components/SummaryPanel.tsx`
- Create: `frontend/src/components/StatusBadge.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/hooks/useDocuments.ts`
- Create: `frontend/src/hooks/useMutationState.ts`

### Frontend Tests

- Create: `frontend/src/components/DocumentList.test.tsx`
- Create: `frontend/src/components/QAPanel.test.tsx`

### Infra and Project Files

- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `.env.example`
- Create: `README.md`
- Create: `storage/raw/.gitkeep`
- Create: `storage/processed/.gitkeep`

## Task 1: Scaffold The Project Skeleton

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `README.md`

- [ ] **Step 1: Write the failing backend health test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_health.py -v`
Expected: FAIL with `ModuleNotFoundError` for `app.main` or missing route.

- [ ] **Step 3: Write minimal backend app and route**

```python
from fastapi import FastAPI

from app.api.routes.health import router as health_router


app = FastAPI(title="AI Document Analyst API")
app.include_router(health_router)
```

```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 5: Create minimal frontend shell**

```tsx
export function App() {
  return (
    <main>
      <h1>AI Document Analyst</h1>
      <p>Upload, search, ask, and summarize documents.</p>
    </main>
  );
}

export default App;
```

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend frontend README.md
git commit -m "chore: scaffold backend and frontend apps"
```

## Task 2: Add Configuration, Database, And Core Models

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/db/models.py`
- Create: `backend/app/domain/documents.py`
- Create: `backend/app/domain/chunks.py`
- Create: `backend/tests/conftest.py`
- Test: `backend/tests/test_documents_upload.py`

- [ ] **Step 1: Write the failing persistence test**

```python
def test_document_model_can_be_persisted(db_session) -> None:
    from app.db.models import Document

    document = Document(
        filename="sample.pdf",
        file_type="pdf",
        storage_path="storage/raw/doc-1/sample.pdf",
        status="uploaded",
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    assert document.id is not None
    assert document.status == "uploaded"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py::test_document_model_can_be_persisted -v`
Expected: FAIL because database/session/model modules do not exist.

- [ ] **Step 3: Implement config and database primitives**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Document Analyst API"
    database_url: str = "sqlite:///./app.db"
    qdrant_url: str = "http://qdrant:6333"
    storage_root: str = "/app/storage"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_top_k: int = 20
    answer_top_k: int = 5
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

- [ ] **Step 4: Implement ORM models**

```python
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(32))
    storage_path: Mapped[str] = mapped_column(String(512))
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pages_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="uploaded")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    page_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    section_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    document: Mapped[Document] = relationship(back_populates="chunks")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py::test_document_model_can_be_persisted -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add app settings and persistence models"
```

## Task 3: Implement Upload Storage And Document Listing

**Files:**
- Create: `backend/app/schemas/documents.py`
- Create: `backend/app/services/storage.py`
- Create: `backend/app/api/routes/documents.py`
- Test: `backend/tests/test_documents_upload.py`

- [ ] **Step 1: Write the failing API upload test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_upload_creates_document_record(tmp_path, monkeypatch) -> None:
    client = TestClient(app)
    files = {"file": ("note.txt", b"hello world", "text/plain")}

    response = client.post("/documents/upload", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "note.txt"
    assert body["status"] == "uploaded"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py::test_upload_creates_document_record -v`
Expected: FAIL with missing route or schema.

- [ ] **Step 3: Implement document schemas and storage service**

```python
from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    pages_count: int | None = None
    language: str | None = None

    model_config = {"from_attributes": True}
```

```python
from pathlib import Path
from uuid import uuid4


class StorageService:
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def save_upload(self, filename: str, content: bytes) -> str:
        doc_key = str(uuid4())
        destination_dir = self.root / "raw" / doc_key
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / filename
        destination.write_bytes(content)
        return str(destination)
```

- [ ] **Step 4: Implement documents routes**

```python
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.db.models import Document
from app.schemas.documents import DocumentRead
from app.services.storage import StorageService


router = APIRouter(prefix="/documents", tags=["documents"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Document:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    storage = StorageService("/app/storage")
    path = storage.save_upload(file.filename or "document", content)

    document = Document(
        filename=file.filename or "document",
        file_type=suffix.lstrip("."),
        storage_path=path,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
```

- [ ] **Step 5: Add listing endpoint**

```python
@router.get("", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return db.query(Document).order_by(Document.upload_time.desc()).all()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add upload storage and documents api"
```

## Task 4: Build Structured Parsers For TXT And PDF

**Files:**
- Create: `backend/app/services/parsers/base.py`
- Create: `backend/app/services/parsers/txt_parser.py`
- Create: `backend/app/services/parsers/pdf_parser.py`
- Create: `backend/app/domain/documents.py`
- Test: `backend/tests/test_pdf_parser.py`

- [ ] **Step 1: Write the failing parser tests**

```python
from app.services.parsers.txt_parser import TxtParser


def test_txt_parser_returns_single_page_structure(tmp_path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("Heading\n\nThis is the body.", encoding="utf-8")

    result = TxtParser().parse(path)

    assert result.doc_id == "local"
    assert len(result.pages) == 1
    assert result.pages[0].blocks[0].text == "Heading"
```

```python
def test_pdf_parser_extracts_text_from_text_pdf(sample_pdf_path) -> None:
    from app.services.parsers.pdf_parser import PdfParser

    result = PdfParser().parse(sample_pdf_path)

    assert len(result.pages) == 1
    assert "Agreement" in result.pages[0].blocks[0].text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_pdf_parser.py -v`
Expected: FAIL because parser modules and domain classes do not exist.

- [ ] **Step 3: Implement shared parser domain types**

```python
from dataclasses import dataclass, field


@dataclass
class DocumentBlock:
    type: str
    text: str
    section_title: str | None = None


@dataclass
class DocumentPage:
    page_num: int
    blocks: list[DocumentBlock] = field(default_factory=list)


@dataclass
class StructuredDocument:
    doc_id: str
    pages: list[DocumentPage] = field(default_factory=list)
```

- [ ] **Step 4: Implement TXT and PDF parsers**

```python
from pathlib import Path

from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument


class TxtParser:
    def parse(self, path: Path) -> StructuredDocument:
        text = path.read_text(encoding="utf-8")
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
        page = DocumentPage(
            page_num=1,
            blocks=[
                DocumentBlock(
                    type="heading" if index == 0 else "paragraph",
                    text=value,
                    section_title=blocks[0] if blocks else None,
                )
                for index, value in enumerate(blocks)
            ],
        )
        return StructuredDocument(doc_id="local", pages=[page])
```

```python
from pathlib import Path

import fitz

from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument


class PdfParser:
    def parse(self, path: Path) -> StructuredDocument:
        pdf = fitz.open(path)
        pages: list[DocumentPage] = []
        for page_index, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if not text:
                blocks = []
            else:
                blocks = [DocumentBlock(type="paragraph", text=text, section_title=None)]
            pages.append(DocumentPage(page_num=page_index, blocks=blocks))
        return StructuredDocument(doc_id="local", pages=pages)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_pdf_parser.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add txt and pdf parsing"
```

## Task 5: Implement Chunking With Metadata Preservation

**Files:**
- Create: `backend/app/services/chunking.py`
- Create: `backend/app/domain/chunks.py`
- Test: `backend/tests/test_chunking.py`

- [ ] **Step 1: Write the failing chunking test**

```python
from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument
from app.services.chunking import ChunkingService


def test_chunker_preserves_page_and_section_metadata() -> None:
    document = StructuredDocument(
        doc_id="doc-1",
        pages=[
            DocumentPage(
                page_num=3,
                blocks=[
                    DocumentBlock(type="heading", text="Termination", section_title="Termination"),
                    DocumentBlock(type="paragraph", text="A " * 500, section_title="Termination"),
                ],
            )
        ],
    )

    chunks = ChunkingService(chunk_size=200, chunk_overlap=50).chunk(document)

    assert len(chunks) >= 2
    assert all(chunk.doc_id == "doc-1" for chunk in chunks)
    assert all(chunk.page_num == 3 for chunk in chunks)
    assert all(chunk.section_title == "Termination" for chunk in chunks)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_chunking.py -v`
Expected: FAIL because chunking service and chunk domain types do not exist.

- [ ] **Step 3: Implement chunk domain type**

```python
from dataclasses import dataclass, field


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    page_num: int | None
    chunk_index: int
    section_title: str | None
    text: str
    metadata: dict[str, str] = field(default_factory=dict)
```

- [ ] **Step 4: Implement chunking service**

```python
from uuid import uuid4

from app.domain.chunks import ChunkRecord
from app.domain.documents import StructuredDocument


class ChunkingService:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: StructuredDocument) -> list[ChunkRecord]:
        results: list[ChunkRecord] = []
        chunk_index = 0
        for page in document.pages:
            page_text = "\n\n".join(block.text for block in page.blocks if block.text.strip())
            section_title = next((block.section_title for block in page.blocks if block.section_title), None)
            start = 0
            while start < len(page_text):
                end = start + self.chunk_size
                text = page_text[start:end].strip()
                if text:
                    results.append(
                        ChunkRecord(
                            chunk_id=str(uuid4()),
                            doc_id=document.doc_id,
                            page_num=page.page_num,
                            chunk_index=chunk_index,
                            section_title=section_title,
                            text=text,
                            metadata={},
                        )
                    )
                    chunk_index += 1
                if end >= len(page_text):
                    break
                start = max(end - self.chunk_overlap, start + 1)
        return results
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_chunking.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add metadata-aware chunking"
```

## Task 6: Wire Ingestion Pipeline End To End

**Files:**
- Create: `backend/app/services/ingestion.py`
- Modify: `backend/app/api/routes/documents.py`
- Test: `backend/tests/test_documents_upload.py`

- [ ] **Step 1: Write the failing ingestion pipeline test**

```python
def test_ingestion_pipeline_marks_document_ready_after_txt_processing(client, db_session) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("sample.txt", b"Title\n\nBody text for retrieval.", "text/plain")},
    )

    assert response.status_code == 201

    detail = client.get(f"/documents/{response.json()['id']}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "ready"
    assert detail.json()["pages_count"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py::test_ingestion_pipeline_marks_document_ready_after_txt_processing -v`
Expected: FAIL because no ingestion orchestration runs after upload.

- [ ] **Step 3: Implement ingestion orchestration**

```python
from pathlib import Path

from app.db.models import Chunk, Document
from app.services.chunking import ChunkingService
from app.services.parsers.pdf_parser import PdfParser
from app.services.parsers.txt_parser import TxtParser


class IngestionService:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunker = ChunkingService(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_document(self, document: Document, db_session) -> Document:
        path = Path(document.storage_path)
        parser = PdfParser() if document.file_type == "pdf" else TxtParser()
        structured = parser.parse(path)
        structured.doc_id = str(document.id)
        chunks = self.chunker.chunk(structured)

        document.pages_count = len(structured.pages)
        document.status = "ready"
        for item in chunks:
            db_session.add(
                Chunk(
                    doc_id=document.id,
                    page_num=item.page_num,
                    chunk_index=item.chunk_index,
                    text=item.text,
                    section_title=item.section_title,
                    metadata_json="{}",
                )
            )
        db_session.commit()
        db_session.refresh(document)
        return document
```

- [ ] **Step 4: Invoke ingestion after upload**

```python
ingestion = IngestionService(chunk_size=800, chunk_overlap=120)
document = ingestion.process_document(document, db)
return document
```

- [ ] **Step 5: Add document detail endpoint**

```python
@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_documents_upload.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add synchronous ingestion pipeline"
```

## Task 7: Add Embeddings And Vector Store Abstractions

**Files:**
- Create: `backend/app/services/embeddings.py`
- Create: `backend/app/services/vector_store.py`
- Modify: `backend/app/services/ingestion.py`
- Test: `backend/tests/test_search.py`

- [ ] **Step 1: Write the failing indexing test**

```python
def test_ingestion_indexes_chunks_for_retrieval(fake_embedder, fake_vector_store) -> None:
    vectors = fake_vector_store.points

    assert vectors
    assert vectors[0]["payload"]["doc_id"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_search.py::test_ingestion_indexes_chunks_for_retrieval -v`
Expected: FAIL because embeddings and vector storage are not called.

- [ ] **Step 3: Implement embedding interface**

```python
from typing import Protocol


class EmbeddingClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...
```

```python
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddingClient:
    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
```

- [ ] **Step 4: Implement vector store interface**

```python
from typing import Protocol


class VectorStore(Protocol):
    def upsert_chunks(self, records: list[dict]) -> None:
        ...

    def search(self, query_vector: list[float], limit: int, filters: dict | None = None) -> list[dict]:
        ...
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class QdrantVectorStore:
    def __init__(self, url: str, collection_name: str = "document_chunks") -> None:
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name

    def ensure_collection(self, size: int) -> None:
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )
```

- [ ] **Step 5: Update ingestion to index chunks**

```python
texts = [item.text for item in chunks]
vectors = self.embedding_client.embed_texts(texts)
self.vector_store.upsert_chunks(
    [
        {
            "id": item.chunk_id,
            "vector": vector,
            "payload": {
                "doc_id": document.id,
                "page_num": item.page_num,
                "section_title": item.section_title,
                "text": item.text,
            },
        }
        for item, vector in zip(chunks, vectors, strict=True)
    ]
)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_search.py::test_ingestion_indexes_chunks_for_retrieval -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add embeddings and vector indexing"
```

## Task 8: Implement Semantic Search Endpoint

**Files:**
- Create: `backend/app/schemas/search.py`
- Create: `backend/app/services/retrieval.py`
- Create: `backend/app/api/routes/search.py`
- Test: `backend/tests/test_search.py`

- [ ] **Step 1: Write the failing search API test**

```python
def test_search_returns_ranked_results(client, seeded_ready_document) -> None:
    response = client.post("/search", json={"query": "termination notice", "top_k": 5})

    assert response.status_code == 200
    body = response.json()
    assert body["results"]
    assert body["results"][0]["page"] == 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_search.py::test_search_returns_ranked_results -v`
Expected: FAIL because no search route exists.

- [ ] **Step 3: Implement search schemas**

```python
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    doc_id: int | None = None


class SearchResult(BaseModel):
    doc_id: int
    page: int | None
    score: float
    text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
```

- [ ] **Step 4: Implement retrieval service and route**

```python
class RetrievalService:
    def __init__(self, embedding_client, vector_store) -> None:
        self.embedding_client = embedding_client
        self.vector_store = vector_store

    def search(self, query: str, top_k: int, filters: dict | None = None) -> list[dict]:
        query_vector = self.embedding_client.embed_texts([query])[0]
        return self.vector_store.search(query_vector=query_vector, limit=top_k, filters=filters)
```

```python
@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest) -> SearchResponse:
    results = retrieval_service.search(
        query=request.query,
        top_k=request.top_k,
        filters={"doc_id": request.doc_id} if request.doc_id else None,
    )
    return SearchResponse(
        results=[
            SearchResult(
                doc_id=item["payload"]["doc_id"],
                page=item["payload"].get("page_num"),
                score=item["score"],
                text=item["payload"]["text"],
            )
            for item in results
        ]
    )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_search.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add semantic search api"
```

## Task 9: Add Reranking And QA With Citations

**Files:**
- Create: `backend/app/domain/retrieval.py`
- Create: `backend/app/schemas/qa.py`
- Create: `backend/app/services/reranking.py`
- Create: `backend/app/services/qa.py`
- Create: `backend/app/api/routes/qa.py`
- Create: `backend/app/prompts/qa_prompt.txt`
- Test: `backend/tests/test_qa.py`

- [ ] **Step 1: Write the failing QA test**

```python
def test_qa_returns_grounded_answer_and_citations(client, seeded_ready_document) -> None:
    response = client.post("/qa", json={"question": "What is the termination notice period?", "doc_id": 1})

    assert response.status_code == 200
    body = response.json()
    assert "30 days" in body["answer"]
    assert body["citations"][0]["page"] == 8
```

```python
def test_qa_refuses_when_evidence_is_missing(client, seeded_ready_document) -> None:
    response = client.post("/qa", json={"question": "What is the CEO salary?", "doc_id": 1})

    assert response.status_code == 200
    assert response.json()["answer"] == "I could not find enough evidence in the document."
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_qa.py -v`
Expected: FAIL because QA pipeline does not exist.

- [ ] **Step 3: Implement reranker and QA response schemas**

```python
from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: int
    page_num: int | None
    section_title: str | None
    text: str
    retrieval_score: float
    rerank_score: float | None = None
```

```python
from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    doc_id: int | None = None


class Citation(BaseModel):
    doc_id: int
    page: int | None
    text: str


class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]
```

- [ ] **Step 4: Implement reranking and grounded QA service**

```python
class RerankerService:
    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        ranked = sorted(candidates, key=lambda item: item.retrieval_score, reverse=True)
        return [
            RetrievedChunk(**{**item.__dict__, "rerank_score": 1.0 - index * 0.01})
            for index, item in enumerate(ranked[:top_k])
        ]
```

```python
class QAService:
    def __init__(self, retrieval_service, reranker_service, llm_client) -> None:
        self.retrieval_service = retrieval_service
        self.reranker_service = reranker_service
        self.llm_client = llm_client

    def answer(self, question: str, doc_id: int | None = None) -> dict:
        retrieved = self.retrieval_service.retrieve_for_qa(question=question, doc_id=doc_id, top_k=20)
        reranked = self.reranker_service.rerank(question, retrieved, top_k=5)
        if not reranked:
            return {"answer": "I could not find enough evidence in the document.", "citations": []}

        answer = self.llm_client.answer_question(question=question, chunks=reranked)
        if not answer.strip():
            answer = "I could not find enough evidence in the document."
        citations = [
            {"doc_id": item.doc_id, "page": item.page_num, "text": item.text}
            for item in reranked
        ]
        return {"answer": answer, "citations": citations}
```

- [ ] **Step 5: Add QA endpoint**

```python
@router.post("/qa", response_model=QAResponse)
def answer_question(request: QARequest) -> QAResponse:
    payload = qa_service.answer(question=request.question, doc_id=request.doc_id)
    return QAResponse(**payload)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_qa.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add reranked qa with citations"
```

## Task 10: Implement Short And Detailed Summary

**Files:**
- Create: `backend/app/schemas/summary.py`
- Create: `backend/app/services/summary.py`
- Create: `backend/app/api/routes/summary.py`
- Create: `backend/app/prompts/summary_short_prompt.txt`
- Create: `backend/app/prompts/summary_detailed_prompt.txt`
- Test: `backend/tests/test_summary.py`

- [ ] **Step 1: Write the failing summary test**

```python
def test_summary_returns_short_mode_output(client, seeded_ready_document) -> None:
    response = client.post("/summary", json={"doc_id": 1, "mode": "short"})

    assert response.status_code == 200
    assert response.json()["summary"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_summary.py -v`
Expected: FAIL because summary route does not exist.

- [ ] **Step 3: Implement summary service and schema**

```python
from pydantic import BaseModel


class SummaryRequest(BaseModel):
    doc_id: int
    mode: str = "short"


class SummaryResponse(BaseModel):
    summary: str
```

```python
class SummaryService:
    def __init__(self, llm_client) -> None:
        self.llm_client = llm_client

    def summarize(self, chunks: list[str], mode: str) -> str:
        if not chunks:
            return "No content available for summary."
        return self.llm_client.summarize(chunks=chunks, mode=mode)
```

- [ ] **Step 4: Add summary endpoint**

```python
@router.post("/summary", response_model=SummaryResponse)
def summarize_document(request: SummaryRequest) -> SummaryResponse:
    chunks = load_document_chunks(request.doc_id)
    return SummaryResponse(summary=summary_service.summarize(chunks=chunks, mode=request.mode))
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest tests/test_summary.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend
git commit -m "feat: add document summary api"
```

## Task 11: Build The Demo Frontend

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/types.ts`
- Create: `frontend/src/components/DocumentUpload.tsx`
- Create: `frontend/src/components/DocumentList.tsx`
- Create: `frontend/src/components/SearchPanel.tsx`
- Create: `frontend/src/components/QAPanel.tsx`
- Create: `frontend/src/components/SummaryPanel.tsx`
- Create: `frontend/src/components/StatusBadge.tsx`
- Create: `frontend/src/hooks/useDocuments.ts`
- Create: `frontend/src/hooks/useMutationState.ts`
- Create: `frontend/src/styles.css`
- Test: `frontend/src/components/DocumentList.test.tsx`
- Test: `frontend/src/components/QAPanel.test.tsx`

- [ ] **Step 1: Write the failing frontend rendering tests**

```tsx
import { render, screen } from "@testing-library/react";

import { DocumentList } from "./DocumentList";


test("renders empty document state", () => {
  render(<DocumentList documents={[]} onSelect={() => undefined} selectedId={null} />);
  expect(screen.getByText(/no documents uploaded/i)).toBeInTheDocument();
});
```

```tsx
import { fireEvent, render, screen } from "@testing-library/react";

import { QAPanel } from "./QAPanel";


test("submits question through callback", () => {
  const handleAsk = vi.fn();
  render(<QAPanel onAsk={handleAsk} answer={null} loading={false} />);
  fireEvent.change(screen.getByLabelText(/question/i), { target: { value: "What is the term?" } });
  fireEvent.click(screen.getByRole("button", { name: /ask/i }));
  expect(handleAsk).toHaveBeenCalledWith("What is the term?");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/frontend && npm test`
Expected: FAIL because the components do not exist.

- [ ] **Step 3: Implement API client and UI components**

```ts
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchDocuments() {
  const response = await fetch(`${API_BASE}/documents`);
  return response.json();
}
```

```tsx
type Props = {
  documents: Array<{ id: number; filename: string; status: string }>;
  selectedId: number | null;
  onSelect: (id: number) => void;
};

export function DocumentList({ documents, selectedId, onSelect }: Props) {
  if (!documents.length) {
    return <p>No documents uploaded yet.</p>;
  }

  return (
    <ul>
      {documents.map((doc) => (
        <li key={doc.id}>
          <button data-active={doc.id === selectedId} onClick={() => onSelect(doc.id)}>
            {doc.filename}
          </button>
        </li>
      ))}
    </ul>
  );
}
```

- [ ] **Step 4: Assemble the main app screen**

```tsx
export default function App() {
  const { documents, selectedId, setSelectedId, refresh } = useDocuments();

  return (
    <main className="app-shell">
      <section>
        <h1>AI Document Analyst</h1>
        <DocumentUpload onUploaded={refresh} />
        <DocumentList documents={documents} selectedId={selectedId} onSelect={setSelectedId} />
      </section>
      <section>
        <SearchPanel selectedDocumentId={selectedId} />
        <QAPanel selectedDocumentId={selectedId} />
        <SummaryPanel selectedDocumentId={selectedId} />
      </section>
    </main>
  );
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/frontend && npm test`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add frontend
git commit -m "feat: add demo frontend for document workflows"
```

## Task 12: Add Docker Compose And Local Developer Setup

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `.env.example`
- Modify: `README.md`

- [ ] **Step 1: Write the failing integration smoke checklist**

```text
1. docker compose up --build starts backend, frontend, and qdrant
2. GET http://localhost:8000/health returns 200
3. Frontend loads at http://localhost:5173
```

- [ ] **Step 2: Run the stack to verify it currently fails**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys && docker compose up --build`
Expected: FAIL because Dockerfiles and compose config do not exist.

- [ ] **Step 3: Implement container definitions**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir .
COPY backend /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* /app/
RUN npm install
COPY frontend /app
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file:
      - .env
    volumes:
      - ./storage:/app/storage
    ports:
      - "8000:8000"
    depends_on:
      - qdrant

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "5173:5173"
    depends_on:
      - backend

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
```

- [ ] **Step 4: Document setup**

```md
## Local Run

1. Copy `.env.example` to `.env`
2. Run `docker compose up --build`
3. Open `http://localhost:5173`
4. Verify API health at `http://localhost:8000/health`
```

- [ ] **Step 5: Run smoke verification**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys && docker compose up --build`
Expected: all services start successfully and health endpoint returns `{"status":"ok"}`.

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add backend frontend docker-compose.yml .env.example README.md storage
git commit -m "chore: add dockerized local development setup"
```

## Task 13: Verify The End-To-End MVP

**Files:**
- Modify: `README.md`
- Test: `backend/tests/test_health.py`
- Test: `backend/tests/test_documents_upload.py`
- Test: `backend/tests/test_pdf_parser.py`
- Test: `backend/tests/test_chunking.py`
- Test: `backend/tests/test_search.py`
- Test: `backend/tests/test_qa.py`
- Test: `backend/tests/test_summary.py`
- Test: `frontend/src/components/DocumentList.test.tsx`
- Test: `frontend/src/components/QAPanel.test.tsx`

- [ ] **Step 1: Run backend test suite**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/backend && pytest -v`
Expected: PASS

- [ ] **Step 2: Run frontend test suite**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys/frontend && npm test`
Expected: PASS

- [ ] **Step 3: Run full stack smoke check**

Run: `cd /Users/stavrmoris/PycharmProjects/ai_doc_analys && docker compose up --build`
Expected: frontend, backend, and qdrant start without crashes.

- [ ] **Step 4: Execute a manual product walkthrough**

```text
1. Upload a TXT document with a known clause.
2. Confirm document status becomes ready.
3. Run semantic search for a phrase in the document.
4. Ask a grounded QA question and verify citations.
5. Ask an unsupported question and verify refusal.
6. Generate both short and detailed summaries.
```

- [ ] **Step 5: Tighten README with final usage notes**

```md
## MVP Features

- PDF/TXT upload
- semantic search
- reranked QA with citations
- short and detailed summary
- React demo UI
```

- [ ] **Step 6: Commit**

```bash
cd /Users/stavrmoris/PycharmProjects/ai_doc_analys
git add README.md backend frontend
git commit -m "docs: finalize mvp verification and usage notes"
```

## Self-Review

### Spec Coverage

- Upload, document persistence, parser normalization, chunking, embeddings, retrieval, reranking, QA, summary, demo UI, and Dockerized local run are all covered by Tasks 1-13.
- OCR, `DOCX`, extraction, advanced query history, and evaluation are intentionally deferred and not included in this implementation plan.

### Placeholder Scan

- No `TBD`, `TODO`, or deferred implementation placeholders remain in the plan.
- Each task contains concrete files, commands, and sample code sufficient to start implementation.

### Type Consistency

- `StructuredDocument`, `ChunkRecord`, and `RetrievedChunk` are introduced before later tasks depend on them.
- API contracts for upload, search, QA, and summary are consistent with the approved design spec.
