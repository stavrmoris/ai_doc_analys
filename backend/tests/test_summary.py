from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FakeSummaryClient:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], str]] = []

    def summarize(self, chunks: list[str], mode: str) -> str:
        self.calls.append((chunks, mode))
        return f"{mode}: {len(chunks)} chunks"


@pytest.fixture
def summary_client(monkeypatch) -> tuple[TestClient, FakeSummaryClient]:
    from app.api.routes import summary as summary_module
    from app.api.routes.summary import router as summary_router
    from app.services.summary import SummaryService

    fake_client = FakeSummaryClient()

    monkeypatch.setattr(
        summary_module,
        "build_summary_service",
        lambda: SummaryService(llm_client=fake_client),
    )
    monkeypatch.setattr(
        summary_module,
        "load_document_chunks",
        lambda doc_id: ["First chunk text.", "Second chunk text."] if doc_id == 1 else [],
    )

    app = FastAPI()
    app.include_router(summary_router)
    return TestClient(app), fake_client


def test_summary_returns_short_mode_output(summary_client) -> None:
    client, fake_client = summary_client

    response = client.post("/summary", json={"doc_id": 1, "mode": "short"})

    assert response.status_code == 200
    assert response.json() == {"summary": "short: 2 chunks"}
    assert fake_client.calls == [(["First chunk text.", "Second chunk text."], "short")]


def test_summary_returns_detailed_mode_output(summary_client) -> None:
    client, fake_client = summary_client

    response = client.post("/summary", json={"doc_id": 1, "mode": "detailed"})

    assert response.status_code == 200
    assert response.json() == {"summary": "detailed: 2 chunks"}
    assert fake_client.calls == [(["First chunk text.", "Second chunk text."], "detailed")]


def test_summary_service_returns_fallback_for_empty_chunks() -> None:
    from app.services.summary import SummaryService

    fake_client = FakeSummaryClient()
    service = SummaryService(llm_client=fake_client)

    response = service.summarize(chunks=[], mode="short")

    assert response == "No content available for summary."
    assert fake_client.calls == []


def test_prompted_summary_client_uses_mode_specific_prompt(tmp_path: Path) -> None:
    from app.services.summary import PromptedSummaryClient

    short_prompt = tmp_path / "short.txt"
    detailed_prompt = tmp_path / "detailed.txt"
    short_prompt.write_text("Short form: {summary}", encoding="utf-8")
    detailed_prompt.write_text("Detailed form: {summary}", encoding="utf-8")

    client = PromptedSummaryClient(short_prompt_path=short_prompt, detailed_prompt_path=detailed_prompt)

    short_summary = client.summarize(["Alpha sentence. Beta sentence."], mode="short")
    detailed_summary = client.summarize(["Alpha sentence. Beta sentence. Gamma sentence."], mode="detailed")

    assert short_summary == "Short form: Alpha sentence."
    assert detailed_summary == "Detailed form: Alpha sentence. Beta sentence. Gamma sentence."


def test_prompted_summary_client_handles_common_punctuation_boundaries() -> None:
    from app.services.summary import PromptedSummaryClient

    client = PromptedSummaryClient()

    short_summary = client.summarize(
        ["Dr. Smith approved version 2.0. What changed? The service now supports uploads! Detailed logs follow."],
        mode="short",
    )
    detailed_summary = client.summarize(
        ["Dr. Smith approved version 2.0. What changed? The service now supports uploads! Detailed logs follow."],
        mode="detailed",
    )

    assert short_summary == "Dr. Smith approved version 2.0."
    assert detailed_summary == "Detailed summary: Dr. Smith approved version 2.0. What changed? The service now supports uploads!"


def test_prompted_summary_client_skips_number_only_headings() -> None:
    from app.services.summary import PromptedSummaryClient

    client = PromptedSummaryClient()

    summary = client.summarize(
        ["1. Заголовок Кейс направлен на создание инструмента прогнозирования спроса. 2. Аннотация."],
        mode="short",
    )

    assert summary == "Заголовок Кейс направлен на создание инструмента прогнозирования спроса."


def test_prompted_summary_client_prefers_openrouter_when_available() -> None:
    from app.services.summary import PromptedSummaryClient

    class FakeOpenRouterClient:
        def complete(self, **kwargs) -> str | None:
            return "LLM summary"

    client = PromptedSummaryClient(openrouter_client=FakeOpenRouterClient())

    summary = client.summarize(["Alpha sentence. Beta sentence."], mode="short")

    assert summary == "LLM summary"
