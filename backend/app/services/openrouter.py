from __future__ import annotations

import json
from typing import Callable
from urllib import request


HttpRequester = Callable[[str, bytes, dict[str, str], float], str]


class OpenRouterChatClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://openrouter.ai/api/v1/chat/completions",
        requester: HttpRequester | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model
        self.base_url = base_url
        self.requester = requester or self._default_requester
        self.timeout_seconds = timeout_seconds

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 300,
    ) -> str | None:
        if not self.api_key:
            return None

        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost/ai-document-analyst",
            "X-Title": "AI Document Analyst",
        }

        try:
            raw_response = self.requester(
                self.base_url,
                json.dumps(payload).encode("utf-8"),
                headers,
                self.timeout_seconds,
            )
        except Exception:
            return None

        try:
            response = json.loads(raw_response)
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            return None

        if isinstance(content, str):
            return content.strip() or None
        if isinstance(content, list):
            text_parts = [
                item.get("text", "").strip()
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            merged = "\n".join(part for part in text_parts if part).strip()
            return merged or None
        return None

    @staticmethod
    def _default_requester(url: str, data: bytes, headers: dict[str, str], timeout: float) -> str:
        http_request = request.Request(url=url, data=data, headers=headers, method="POST")
        with request.urlopen(http_request, timeout=timeout) as response:
            return response.read().decode("utf-8")


__all__ = ["HttpRequester", "OpenRouterChatClient"]
