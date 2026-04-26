from app.services.openrouter import OpenRouterChatClient


def test_openrouter_client_returns_none_without_api_key() -> None:
    client = OpenRouterChatClient(api_key="", model="openai/gpt-4o-mini")

    response = client.complete(system_prompt="system", user_prompt="user")

    assert response is None


def test_openrouter_client_extracts_string_content() -> None:
    def fake_requester(url: str, data: bytes, headers: dict[str, str], timeout: float) -> str:
        assert "Authorization" in headers
        assert timeout == 30.0
        return '{"choices":[{"message":{"content":"Grounded answer"}}]}'

    client = OpenRouterChatClient(
        api_key="secret",
        model="openai/gpt-4o-mini",
        requester=fake_requester,
    )

    response = client.complete(system_prompt="system", user_prompt="user")

    assert response == "Grounded answer"


def test_openrouter_client_extracts_text_from_content_parts() -> None:
    def fake_requester(url: str, data: bytes, headers: dict[str, str], timeout: float) -> str:
        return (
            '{"choices":[{"message":{"content":['
            '{"type":"text","text":"Line 1"},'
            '{"type":"text","text":"Line 2"}]}}]}'
        )

    client = OpenRouterChatClient(
        api_key="secret",
        model="openai/gpt-4o-mini",
        requester=fake_requester,
    )

    response = client.complete(system_prompt="system", user_prompt="user")

    assert response == "Line 1\nLine 2"
