from __future__ import annotations

import hashlib
import math
from typing import Protocol

from app.core.config import settings
from app.services.text_normalization import tokenize_text


class EmbeddingClient(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...


class HashingEmbeddingClient:
    def __init__(self, dimensions: int = 384) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in self._tokenize(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return list(tokenize_text(text))


class SentenceTransformerEmbeddingClient:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - depends on optional package
                raise RuntimeError(
                    "sentence-transformers is required to use SentenceTransformerEmbeddingClient"
                ) from exc

            self._model = SentenceTransformer(self.model_name)

        return self._model.encode(texts, normalize_embeddings=True).tolist()


def build_default_embedding_client() -> EmbeddingClient:
    if settings.embedding_model_name.startswith("hashing"):
        _, _, dimension_text = settings.embedding_model_name.partition("-")
        dimensions = int(dimension_text) if dimension_text else 384
        return HashingEmbeddingClient(dimensions=dimensions)

    return SentenceTransformerEmbeddingClient(settings.embedding_model_name)


__all__ = [
    "EmbeddingClient",
    "HashingEmbeddingClient",
    "SentenceTransformerEmbeddingClient",
    "build_default_embedding_client",
]
