import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.retrieval import RetrievedChunk
from app.services.qa import GroundedAnswerResult


class FakeRetrievalService:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self.results = results
        self.calls: list[tuple[str, int | None, int]] = []

    def retrieve_for_qa(
        self,
        question: str,
        doc_id: int | None = None,
        top_k: int = 20,
    ) -> list[RetrievedChunk]:
        self.calls.append((question, doc_id, top_k))
        return self.results


class FakeRerankerService:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self.results = results
        self.calls: list[tuple[str, list[RetrievedChunk], int]] = []

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        self.calls.append((query, candidates, top_k))
        return self.results


class FakeLLMClient:
    def __init__(self, answer: GroundedAnswerResult | None) -> None:
        self.answer = answer
        self.calls: list[tuple[str, list[RetrievedChunk]]] = []

    def answer_question(self, question: str, chunks: list[RetrievedChunk]) -> GroundedAnswerResult | None:
        self.calls.append((question, chunks))
        return self.answer


@pytest.fixture
def qa_client(monkeypatch) -> tuple[TestClient, FakeRetrievalService, FakeRerankerService, FakeLLMClient]:
    from app.api.routes import qa as qa_module
    from app.api.routes.qa import router as qa_router
    from app.services.qa import QAService

    retrieval = FakeRetrievalService(
        results=[
            RetrievedChunk(
                chunk_id="chunk-1",
                doc_id=1,
                page_num=8,
                section_title="Termination",
                text="The agreement may be terminated with 30 days prior notice.",
                retrieval_score=0.92,
            ),
            RetrievedChunk(
                chunk_id="chunk-2",
                doc_id=1,
                page_num=9,
                section_title="Renewal",
                text="Renewal is automatic unless either party objects.",
                retrieval_score=0.73,
            ),
        ]
    )
    reranker = FakeRerankerService(
        results=[
            RetrievedChunk(
                chunk_id="chunk-1",
                doc_id=1,
                page_num=8,
                section_title="Termination",
                text="The agreement may be terminated with 30 days prior notice.",
                retrieval_score=0.92,
                rerank_score=0.99,
            ),
            RetrievedChunk(
                chunk_id="chunk-2",
                doc_id=1,
                page_num=9,
                section_title="Renewal",
                text="Renewal is automatic unless either party objects.",
                retrieval_score=0.73,
                rerank_score=0.88,
            ),
        ]
    )
    llm_client = FakeLLMClient(
        answer=GroundedAnswerResult(
            answer="The termination notice period is 30 days.",
            supporting_chunks=[reranker.results[0]],
        )
    )

    monkeypatch.setattr(
        qa_module,
        "build_qa_service",
        lambda: QAService(
            retrieval_service=retrieval,
            reranker_service=reranker,
            llm_client=llm_client,
        ),
    )

    app = FastAPI()
    app.include_router(qa_router)
    return TestClient(app), retrieval, reranker, llm_client


def test_qa_returns_grounded_answer_and_citations(qa_client) -> None:
    client, retrieval, reranker, llm_client = qa_client

    response = client.post("/qa", json={"question": "What is the termination notice period?", "doc_id": 1})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "The termination notice period is 30 days.",
        "citations": [
            {
                "doc_id": 1,
                "page": 8,
                "text": "The agreement may be terminated with 30 days prior notice.",
            },
        ],
    }
    assert retrieval.calls == [("What is the termination notice period?", 1, 20)]
    assert reranker.calls[0][0] == "What is the termination notice period?"
    assert reranker.calls[0][2] == 5
    assert llm_client.calls[0][0] == "What is the termination notice period?"


def test_qa_refuses_when_evidence_is_missing(monkeypatch) -> None:
    from app.api.routes import qa as qa_module
    from app.api.routes.qa import router as qa_router
    from app.services.qa import QAService

    retrieval = FakeRetrievalService(results=[])
    reranker = FakeRerankerService(results=[])
    llm_client = FakeLLMClient(answer=None)

    monkeypatch.setattr(
        qa_module,
        "build_qa_service",
        lambda: QAService(
            retrieval_service=retrieval,
            reranker_service=reranker,
            llm_client=llm_client,
        ),
    )

    app = FastAPI()
    app.include_router(qa_router)
    client = TestClient(app)

    response = client.post("/qa", json={"question": "What is the CEO salary?", "doc_id": 1})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "I could not find enough evidence in the document.",
        "citations": [],
    }
    assert retrieval.calls == [("What is the CEO salary?", 1, 20)]
    assert reranker.calls == [("What is the CEO salary?", [], 5)]
    assert llm_client.calls == []


def test_qa_refuses_when_overlap_is_too_weak(monkeypatch) -> None:
    from app.api.routes import qa as qa_module
    from app.api.routes.qa import router as qa_router
    from app.services.qa import PromptedGroundedAnswerClient, QAService

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-weak-1",
            doc_id=1,
            page_num=4,
            section_title="Termination",
            text="The contract includes termination obligations for both parties.",
            retrieval_score=0.8,
            rerank_score=0.8,
        ),
        RetrievedChunk(
            chunk_id="chunk-weak-2",
            doc_id=1,
            page_num=6,
            section_title="Payments",
            text="The payment period is monthly and invoiced in advance.",
            retrieval_score=0.7,
            rerank_score=0.7,
        ),
    ]
    retrieval = FakeRetrievalService(results=retrieved)
    reranker = FakeRerankerService(results=retrieved)
    llm_client = PromptedGroundedAnswerClient()

    monkeypatch.setattr(
        qa_module,
        "build_qa_service",
        lambda: QAService(
            retrieval_service=retrieval,
            reranker_service=reranker,
            llm_client=llm_client,
        ),
    )

    app = FastAPI()
    app.include_router(qa_router)
    client = TestClient(app)

    response = client.post("/qa", json={"question": "What is the termination notice period?", "doc_id": 1})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "I could not find enough evidence in the document.",
        "citations": [],
    }


def test_prompted_grounded_answer_client_accepts_supported_morphological_match() -> None:
    from app.services.qa import PromptedGroundedAnswerClient, QAService

    supported_chunk = RetrievedChunk(
        chunk_id="chunk-supported",
        doc_id=1,
        page_num=8,
        section_title="Termination",
        text="The agreement may be terminated with 30 days prior notice.",
        retrieval_score=0.95,
        rerank_score=0.95,
    )
    unrelated_chunk = RetrievedChunk(
        chunk_id="chunk-unrelated",
        doc_id=1,
        page_num=9,
        section_title="Renewal",
        text="Renewal is automatic unless either party objects.",
        retrieval_score=0.7,
        rerank_score=0.7,
    )

    service = QAService(
        retrieval_service=FakeRetrievalService(results=[supported_chunk, unrelated_chunk]),
        reranker_service=FakeRerankerService(results=[supported_chunk, unrelated_chunk]),
        llm_client=PromptedGroundedAnswerClient(),
    )

    response = service.answer(question="What is the termination notice period?", doc_id=1)

    assert response.model_dump() == {
        "answer": "The agreement may be terminated with 30 days prior notice.",
        "citations": [
            {
                "doc_id": 1,
                "page": 8,
                "text": "The agreement may be terminated with 30 days prior notice.",
            }
        ],
    }


def test_prompted_grounded_answer_client_prefers_openrouter_when_available() -> None:
    from app.services.qa import PromptedGroundedAnswerClient

    class FakeOpenRouterClient:
        def complete(self, **kwargs) -> str | None:
            return "The notice period is 30 days."

    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            doc_id=1,
            page_num=8,
            section_title="Termination",
            text="The agreement may be terminated with 30 days prior notice.",
            retrieval_score=0.92,
            rerank_score=0.99,
        ),
        RetrievedChunk(
            chunk_id="chunk-2",
            doc_id=1,
            page_num=9,
            section_title="Renewal",
            text="Renewal is automatic unless either party objects.",
            retrieval_score=0.73,
            rerank_score=0.88,
        ),
    ]

    client = PromptedGroundedAnswerClient(openrouter_client=FakeOpenRouterClient())

    result = client.answer_question("What is the termination notice period?", chunks)

    assert result is not None
    assert result.answer == "The notice period is 30 days."
    assert [chunk.chunk_id for chunk in result.supporting_chunks] == ["chunk-1"]


def test_prompted_grounded_answer_client_matches_russian_word_forms() -> None:
    from app.services.qa import PromptedGroundedAnswerClient

    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            doc_id=1,
            page_num=2,
            section_title="Timeline",
            text="Спринт 1 длится 3 недели.",
            retrieval_score=0.9,
            rerank_score=0.9,
        ),
    ]

    result = PromptedGroundedAnswerClient().answer_question("Сколько длится неделя спринта?", chunks)

    assert result is not None
    assert result.answer == "Спринт 1 длится 3 недели."
