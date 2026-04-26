import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.services.embeddings import HashingEmbeddingClient, build_default_embedding_client
from app.services.retrieval import RetrievalResult, RetrievalService
from app.services.vector_store import QdrantVectorStore


class FakeRetrievalService:
    def __init__(self, results: list[RetrievalResult]) -> None:
        self.results = results
        self.calls: list[tuple[str, int, int | None]] = []

    def search(self, query: str, limit: int, doc_id: int | None = None) -> list[RetrievalResult]:
        self.calls.append((query, limit, doc_id))
        return self.results


class FakeEmbedder:
    def __init__(self, vector: list[float]) -> None:
        self.vector = vector
        self.calls: list[list[str]] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [self.vector for _ in texts]


class FakeVectorStore:
    def __init__(self, results: list[dict]) -> None:
        self.results = results
        self.calls: list[tuple[list[float], int, dict | None]] = []

    def search(self, query_vector: list[float], limit: int, filters: dict | None = None) -> list[dict]:
        self.calls.append((query_vector, limit, filters))
        return self.results


@pytest.fixture
def search_client(monkeypatch) -> tuple[TestClient, FakeRetrievalService]:
    from app.api.routes import search as search_module
    from app.api.routes.search import router as search_router

    retrieval = FakeRetrievalService(
        results=[
            RetrievalResult(
                doc_id=7,
                page_num=3,
                section_title="Findings",
                text="Relevant paragraph",
                score=0.91,
            ),
            RetrievalResult(
                doc_id=4,
                page_num=1,
                section_title=None,
                text="Another match",
                score=0.73,
            ),
        ]
    )
    monkeypatch.setattr(search_module, "build_retrieval_service", lambda: retrieval)

    app = FastAPI()
    app.include_router(search_router)
    return TestClient(app), retrieval


def test_retrieval_service_embeds_query_and_passes_doc_id_filter() -> None:
    embedder = FakeEmbedder([0.4, 0.5, 0.6])
    vector_store = FakeVectorStore(
        results=[
            {
                "payload": {
                    "doc_id": 11,
                    "page_num": 2,
                    "section_title": "Summary",
                    "text": "Matched text",
                },
                "score": 0.88,
            }
        ]
    )

    service = RetrievalService(embedding_client=embedder, vector_store=vector_store)

    results = service.search("needle", limit=5, doc_id=11)

    assert embedder.calls == [["needle"]]
    assert vector_store.calls == [([0.4, 0.5, 0.6], 5, {"doc_id": 11})]
    assert results == [
        RetrievalResult(
            doc_id=11,
            page_num=2,
            section_title="Summary",
            text="Matched text",
            score=0.88,
        )
    ]


def test_retrieval_service_adds_lexical_matches_from_database(db_engine, monkeypatch) -> None:
    from app.core.database import create_session_factory
    from app.db.models import Chunk, Document
    from app.services import retrieval as retrieval_module

    session_factory = create_session_factory(db_engine)
    monkeypatch.setattr(retrieval_module, "SessionLocal", session_factory)

    db = session_factory()
    try:
        document = Document(filename="case.pdf", file_type="pdf", storage_path="/tmp/case.pdf", status="ready")
        db.add(document)
        db.flush()
        db.add_all(
            [
                Chunk(
                    doc_id=document.id,
                    page_num=1,
                    chunk_index=0,
                    text="Показ 3: обученная нейросетевая модель показывает результаты лучше бейзлайна.",
                    section_title=None,
                    metadata_json="{}",
                ),
                Chunk(
                    doc_id=document.id,
                    page_num=2,
                    chunk_index=1,
                    text="Нужно предоставить итоговый результат: CSV-файл с данными и Jupyter Notebook с графиками.",
                    section_title=None,
                    metadata_json="{}",
                ),
            ]
        )
        db.commit()
        doc_id = document.id
    finally:
        db.close()

    service = RetrievalService(
        embedding_client=FakeEmbedder([0.1, 0.2, 0.3]),
        vector_store=FakeVectorStore(results=[]),
    )

    results = service.search("какие результаты нужно предоставить", limit=1, doc_id=doc_id)

    assert results[0].text.startswith("Нужно предоставить итоговый результат")


def test_retrieval_service_matches_russian_word_forms(db_engine, monkeypatch) -> None:
    from app.core.database import create_session_factory
    from app.db.models import Chunk, Document
    from app.services import retrieval as retrieval_module

    session_factory = create_session_factory(db_engine)
    monkeypatch.setattr(retrieval_module, "SessionLocal", session_factory)

    db = session_factory()
    try:
        document = Document(filename="schedule.pdf", file_type="pdf", storage_path="/tmp/schedule.pdf", status="ready")
        db.add(document)
        db.flush()
        db.add(
            Chunk(
                doc_id=document.id,
                page_num=1,
                chunk_index=0,
                text="Спринт 1 (Недели 1-3): Данные и анализ.",
                section_title=None,
                metadata_json="{}",
            )
        )
        db.commit()
        doc_id = document.id
    finally:
        db.close()

    service = RetrievalService(
        embedding_client=FakeEmbedder([0.1, 0.2, 0.3]),
        vector_store=FakeVectorStore(results=[]),
    )

    results = service.search("неделя", limit=1, doc_id=doc_id)

    assert results
    assert "Недели 1-3" in results[0].text


def test_default_embedding_client_is_lightweight_hashing_client() -> None:
    client = build_default_embedding_client()

    assert isinstance(client, HashingEmbeddingClient)
    assert len(client.embed_texts(["termination notice"])[0]) == 384


def test_search_route_returns_ranked_results(search_client) -> None:
    client, retrieval = search_client

    response = client.post("/search", json={"query": "hello world", "limit": 2})

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "doc_id": 7,
                "page_num": 3,
                "section_title": "Findings",
                "text": "Relevant paragraph",
                "score": 0.91,
            },
            {
                "doc_id": 4,
                "page_num": 1,
                "section_title": None,
                "text": "Another match",
                "score": 0.73,
            },
        ]
    }
    assert retrieval.calls == [("hello world", 2, None)]


def test_qdrant_vector_store_returns_empty_when_collection_missing() -> None:
    class FakeQdrantClient:
        def collection_exists(self, collection_name: str) -> bool:
            return False

    vector_store = QdrantVectorStore.__new__(QdrantVectorStore)
    vector_store.client = FakeQdrantClient()
    vector_store.collection_name = "document_chunks"

    assert vector_store.search(query_vector=[0.1, 0.2], limit=5) == []


def test_qdrant_vector_store_converts_chunk_ids_to_valid_point_ids() -> None:
    class FakeQdrantClient:
        def __init__(self) -> None:
            self.points = None

        def collection_exists(self, collection_name: str) -> bool:
            return True

        def upsert(self, collection_name: str, points: list[dict]) -> None:
            self.points = points

    client = FakeQdrantClient()
    vector_store = QdrantVectorStore.__new__(QdrantVectorStore)
    vector_store.client = client
    vector_store.collection_name = "document_chunks"
    vector_store._collection_ready = False

    vector_store.upsert_chunks(
        [
            {
                "id": "1:1:0",
                "vector": [0.1, 0.2, 0.3],
                "payload": {"doc_id": 1, "text": "hello"},
            }
        ]
    )

    assert client.points is not None
    assert client.points[0]["id"] != "1:1:0"
    assert client.points[0]["id"].count("-") == 4
    assert client.points[0]["payload"]["chunk_id"] == "1:1:0"


def test_qdrant_vector_store_search_uses_query_points_when_search_is_unavailable() -> None:
    class FakeQueryResponse:
        points = [{"payload": {"doc_id": 1, "text": "hello"}, "score": 0.8}]

    class FakeQdrantClient:
        def __init__(self) -> None:
            self.query = None

        def collection_exists(self, collection_name: str) -> bool:
            return True

        def query_points(self, **kwargs):
            self.query = kwargs
            return FakeQueryResponse()

    client = FakeQdrantClient()
    vector_store = QdrantVectorStore.__new__(QdrantVectorStore)
    vector_store.client = client
    vector_store.collection_name = "document_chunks"

    results = vector_store.search(query_vector=[0.1, 0.2], limit=3)

    assert results == FakeQueryResponse.points
    assert client.query["collection_name"] == "document_chunks"
    assert client.query["query"] == [0.1, 0.2]
    assert client.query["limit"] == 3


def test_qdrant_vector_store_returns_empty_when_client_is_unavailable() -> None:
    class FailingQdrantClient:
        def collection_exists(self, collection_name: str) -> bool:
            raise RuntimeError("qdrant offline")

    vector_store = QdrantVectorStore.__new__(QdrantVectorStore)
    vector_store.client = FailingQdrantClient()
    vector_store.collection_name = "document_chunks"

    assert vector_store.search(query_vector=[0.1, 0.2], limit=3) == []


def test_search_route_is_exposed_on_main_app_and_returns_empty_results(monkeypatch) -> None:
    from app.services import retrieval as retrieval_module
    from app.main import app

    class EmptyQdrantClient:
        def collection_exists(self, collection_name: str) -> bool:
            return False

    vector_store = QdrantVectorStore.__new__(QdrantVectorStore)
    vector_store.client = EmptyQdrantClient()
    vector_store.collection_name = "document_chunks"

    embedder = FakeEmbedder([0.7, 0.8, 0.9])
    monkeypatch.setattr(retrieval_module, "build_default_embedding_client", lambda: embedder)
    monkeypatch.setattr(retrieval_module, "build_default_vector_store", lambda: vector_store)

    client = TestClient(app)
    response = client.post("/search", json={"query": "missing", "limit": 3})

    assert response.status_code == 200
    assert response.json() == {"results": []}
    assert embedder.calls == [["missing"]]


def test_build_default_vector_store_falls_back_to_noop_when_qdrant_is_unavailable(monkeypatch) -> None:
    from app.services import vector_store as vector_store_module

    monkeypatch.setattr(
        vector_store_module,
        "QdrantVectorStore",
        lambda url: (_ for _ in ()).throw(RuntimeError("qdrant unavailable")),
    )

    store = vector_store_module.build_default_vector_store()

    assert store.__class__.__name__ == "NoOpVectorStore"
