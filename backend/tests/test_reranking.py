from app.domain.retrieval import RetrievedChunk
from app.services.reranking import RerankerService


def test_reranker_boosts_lexically_relevant_russian_chunks() -> None:
    service = RerankerService()
    weak_vector_match = RetrievedChunk(
        chunk_id="weak",
        doc_id=1,
        page_num=1,
        section_title=None,
        text="Показ 3: обученная нейросетевая модель показывает результаты лучше бейзлайна.",
        retrieval_score=0.30,
    )
    relevant_match = RetrievedChunk(
        chunk_id="relevant",
        doc_id=1,
        page_num=1,
        section_title=None,
        text="Цель выполнения кейса: разработать прототип сервиса прогнозирования спроса.",
        retrieval_score=0.20,
    )

    result = service.rerank(
        query="какая цель кейса прогнозирование спроса",
        candidates=[weak_vector_match, relevant_match],
        top_k=2,
    )

    assert result[0].chunk_id == "relevant"
    assert result[0].rerank_score is not None


def test_reranker_prefers_intent_block_over_short_title() -> None:
    service = RerankerService()
    title = RetrievedChunk(
        chunk_id="title",
        doc_id=1,
        page_num=1,
        section_title=None,
        text="Название кейса: Нейросетевая модель для прогнозирования спроса на товары.",
        retrieval_score=0.25,
    )
    goal = RetrievedChunk(
        chunk_id="goal",
        doc_id=1,
        page_num=1,
        section_title=None,
        text="Цель выполнения кейса: разработать прототип сервиса, который предсказывает спрос.",
        retrieval_score=0.20,
    )

    result = service.rerank(
        query="какая цель кейса прогнозирование спроса",
        candidates=[title, goal],
        top_k=2,
    )

    assert result[0].chunk_id == "goal"
