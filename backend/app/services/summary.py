from __future__ import annotations

from pathlib import Path
import re
from typing import Protocol

from app.services.openrouter import OpenRouterChatClient

EMPTY_SUMMARY = "No content available for summary."


class SummaryClient(Protocol):
    def summarize(self, chunks: list[str], mode: str) -> str:
        ...


class PromptedSummaryClient:
    def __init__(
        self,
        short_prompt_path: Path | None = None,
        detailed_prompt_path: Path | None = None,
        openrouter_client: OpenRouterChatClient | None = None,
    ) -> None:
        prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self.short_prompt_path = short_prompt_path or prompts_dir / "summary_short_prompt.txt"
        self.detailed_prompt_path = detailed_prompt_path or prompts_dir / "summary_detailed_prompt.txt"
        self._prompt_templates: dict[str, str] = {}
        self.openrouter_client = openrouter_client

    def summarize(self, chunks: list[str], mode: str) -> str:
        context = self._normalize_chunks(chunks)
        llm_summary = self._summarize_with_openrouter(context=context, mode=mode)
        if llm_summary:
            return llm_summary

        prompt_template = self._get_prompt_template(mode)
        sentences = self._split_sentences(context)
        if not sentences:
            return EMPTY_SUMMARY

        sentence_limit = 1 if mode == "short" else min(3, len(sentences))
        summary = " ".join(sentences[:sentence_limit]).strip()
        return prompt_template.format(context=context, summary=summary).strip()

    def _summarize_with_openrouter(self, *, context: str, mode: str) -> str | None:
        if self.openrouter_client is None:
            return None
        if not context.strip():
            return None

        style = "brief executive summary in 2-3 sentences" if mode == "short" else "detailed but concise summary in 4-6 sentences"
        prompt = (
            "Summarize the following document excerpt. "
            "Stay factual, do not invent missing information, and preserve the document language. "
            f"Return only the summary as a {style}.\n\n"
            f"Document context:\n{context[:12000]}"
        )
        return self.openrouter_client.complete(
            system_prompt="You are a precise document analyst who writes grounded summaries.",
            user_prompt=prompt,
            temperature=0.1,
            max_tokens=280 if mode == "short" else 500,
        )

    def _get_prompt_template(self, mode: str) -> str:
        prompt_path = self.short_prompt_path if mode == "short" else self.detailed_prompt_path
        cache_key = str(prompt_path)
        if cache_key not in self._prompt_templates:
            self._prompt_templates[cache_key] = prompt_path.read_text(encoding="utf-8").strip()
        return self._prompt_templates[cache_key]

    @staticmethod
    def _normalize_chunks(chunks: list[str]) -> str:
        return " ".join(chunk.strip() for chunk in chunks if chunk.strip())

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        normalized = text.replace("\n", " ")
        protected = re.sub(r"(?<=\d)\.(?=\d)", "<DOT>", normalized)
        for abbreviation in ("Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "e.g.", "i.e.", "U.S."):
            protected = protected.replace(abbreviation, abbreviation.replace(".", "<DOT>"))

        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", protected) if part.strip()]
        return [
            sentence
            for part in parts
            if (sentence := part.replace("<DOT>", ".")).strip()
            and PromptedSummaryClient._is_content_sentence(sentence)
        ]

    @staticmethod
    def _is_content_sentence(sentence: str) -> bool:
        normalized = sentence.strip()
        alpha_count = sum(char.isalpha() for char in normalized)
        if alpha_count < 4:
            return False
        if re.fullmatch(r"\d+[\s.)]*", normalized):
            return False
        return True


class SummaryService:
    def __init__(self, llm_client: SummaryClient) -> None:
        self.llm_client = llm_client

    def summarize(self, chunks: list[str], mode: str) -> str:
        if not any(chunk.strip() for chunk in chunks):
            return EMPTY_SUMMARY
        return self.llm_client.summarize(chunks=chunks, mode=mode)


__all__ = [
    "EMPTY_SUMMARY",
    "PromptedSummaryClient",
    "SummaryClient",
    "SummaryService",
]
