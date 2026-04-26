from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.documents import get_db, router as documents_router
from app.core.database import create_session_factory
from app.services.ingestion import IngestionService


class FakeEmbedder:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeVectorStore:
    def __init__(self) -> None:
        self.deleted_doc_ids: list[int] = []

    def upsert_chunks(self, records: list[dict]) -> None:
        return None

    def delete_document(self, doc_id: int) -> None:
        self.deleted_doc_ids.append(doc_id)


@pytest.fixture
def documents_client(db_engine, tmp_path, monkeypatch) -> TestClient:
    from app.api.routes import documents as documents_module

    storage_root = tmp_path / "storage"
    fake_vector_store = FakeVectorStore()
    monkeypatch.setattr(documents_module.settings, "storage_root", str(storage_root))
    monkeypatch.setattr(
        documents_module,
        "build_ingestion_service",
        lambda: IngestionService(
            embedding_client=FakeEmbedder(),
            vector_store=fake_vector_store,
        ),
    )
    monkeypatch.setattr(documents_module, "build_default_vector_store", lambda: fake_vector_store)

    session_factory = create_session_factory(db_engine)
    app = FastAPI()
    app.include_router(documents_router)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_upload_creates_document_record(documents_client, db_engine, tmp_path) -> None:
    files = {"file": ("note.txt", b"hello world", "text/plain")}

    response = documents_client.post("/documents/upload", files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "note.txt"
    assert body["file_type"] == "txt"
    assert body["status"] == "ready"
    assert body["pages_count"] == 1

    storage_path = Path(body["storage_path"])
    assert storage_path.is_file()
    assert storage_path.read_text() == "hello world"
    assert str(storage_path).startswith(str(tmp_path / "storage"))

    session_factory = create_session_factory(db_engine)
    db = session_factory()
    try:
        from app.db.models import Chunk, Document

        document = db.query(Document).one()
        assert document.filename == "note.txt"
        assert document.status == "ready"
        assert document.pages_count == 1

        chunks = db.query(Chunk).order_by(Chunk.chunk_index.asc()).all()
        assert len(chunks) == 1
        assert chunks[0].doc_id == document.id
        assert chunks[0].page_num == 1
        assert chunks[0].chunk_index == 0
        assert chunks[0].text == "hello world"
    finally:
        db.close()


def test_get_document_returns_processed_document(documents_client) -> None:
    response = documents_client.post(
        "/documents/upload",
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 201
    document_id = response.json()["id"]

    detail_response = documents_client.get(f"/documents/{document_id}")

    assert detail_response.status_code == 200
    assert detail_response.json() == response.json()


def test_list_documents_returns_most_recent_first(documents_client, db_engine) -> None:
    from app.db.models import Document

    session_factory = create_session_factory(db_engine)
    db = session_factory()
    try:
        older = Document(
            filename="older.txt",
            file_type="txt",
            storage_path="/tmp/older.txt",
            status="uploaded",
            upload_time=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=10),
        )
        newer = Document(
            filename="newer.txt",
            file_type="txt",
            storage_path="/tmp/newer.txt",
            status="uploaded",
            upload_time=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db.add_all([older, newer])
        db.commit()
    finally:
        db.close()

    response = documents_client.get("/documents")

    assert response.status_code == 200
    body = response.json()
    assert [item["filename"] for item in body] == ["newer.txt", "older.txt"]


def test_upload_removes_saved_file_when_commit_fails(db_engine, tmp_path, monkeypatch) -> None:
    from app.api.routes.documents import get_db, router as documents_router
    from app.api.routes import documents as documents_module

    storage_root = tmp_path / "storage"
    monkeypatch.setattr(documents_module.settings, "storage_root", str(storage_root))
    monkeypatch.setattr(
        documents_module,
        "build_ingestion_service",
        lambda: IngestionService(
            embedding_client=FakeEmbedder(),
            vector_store=FakeVectorStore(),
        ),
    )

    session_factory = create_session_factory(db_engine)
    app = FastAPI()
    app.include_router(documents_router)

    def override_get_db():
        db = session_factory()

        def failing_commit() -> None:
            raise RuntimeError("commit failed")

        monkeypatch.setattr(db, "commit", failing_commit)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/documents/upload", files={"file": ("note.txt", b"hello world", "text/plain")})

    assert response.status_code == 500
    assert not any(path.is_file() for path in storage_root.rglob("*"))

    db = session_factory()
    try:
        from app.db.models import Document

        assert db.query(Document).count() == 0
    finally:
        db.close()


def test_upload_rolls_back_document_and_file_when_ingestion_fails(db_engine, tmp_path, monkeypatch) -> None:
    from app.api.routes.documents import get_db, router as documents_router
    from app.api.routes import documents as documents_module

    storage_root = tmp_path / "storage"
    monkeypatch.setattr(documents_module.settings, "storage_root", str(storage_root))

    class FailingIngestionService:
        def ingest_document(self, db, document) -> None:
            raise RuntimeError("ingestion failed")

    monkeypatch.setattr(documents_module, "build_ingestion_service", lambda: FailingIngestionService())

    session_factory = create_session_factory(db_engine)
    app = FastAPI()
    app.include_router(documents_router)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post("/documents/upload", files={"file": ("note.txt", b"hello world", "text/plain")})

    assert response.status_code == 500
    assert response.json() == {"detail": "Document ingestion failed"}
    assert not any(path.is_file() for path in storage_root.rglob("*"))

    db = session_factory()
    try:
        from app.db.models import Chunk, Document

        assert db.query(Document).count() == 0
        assert db.query(Chunk).count() == 0
    finally:
        db.close()


def test_delete_document_removes_record_chunks_file_and_vector_entries(documents_client, db_engine) -> None:
    upload_response = documents_client.post(
        "/documents/upload",
        files={"file": ("note.txt", b"hello world", "text/plain")},
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]
    storage_path = Path(upload_response.json()["storage_path"])
    assert storage_path.exists()

    delete_response = documents_client.delete(f"/documents/{document_id}")

    assert delete_response.status_code == 204
    assert not storage_path.exists()

    session_factory = create_session_factory(db_engine)
    db = session_factory()
    try:
        from app.db.models import Chunk, Document

        assert db.query(Document).count() == 0
        assert db.query(Chunk).count() == 0
    finally:
        db.close()


def test_delete_document_returns_not_found_for_missing_id(documents_client) -> None:
    response = documents_client.delete("/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
