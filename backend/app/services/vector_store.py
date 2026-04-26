from __future__ import annotations

from typing import Any, Protocol
from uuid import NAMESPACE_URL, uuid5

from app.core.config import settings


class VectorStore(Protocol):
    def upsert_chunks(self, records: list[dict[str, Any]]) -> None:
        ...

    def delete_document(self, doc_id: int) -> None:
        ...

    def search(
        self,
        query_vector: list[float],
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        ...


class NoOpVectorStore:
    def upsert_chunks(self, records: list[dict[str, Any]]) -> None:
        return None

    def delete_document(self, doc_id: int) -> None:
        del doc_id
        return None

    def search(
        self,
        query_vector: list[float],
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        return []


class QdrantVectorStore:
    def __init__(self, url: str, collection_name: str = "document_chunks") -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError("qdrant-client is required to use QdrantVectorStore") from exc

        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self._distance = Distance
        self._vector_params = VectorParams
        self._collection_ready = False

    def ensure_collection(self, size: int) -> None:
        if size <= 0:
            raise ValueError("vector size must be positive")
        if self._collection_ready:
            return

        try:
            collection_exists = self.client.collection_exists(self.collection_name)
        except Exception:
            return
        if not collection_exists:
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=self._vector_params(size=size, distance=self._distance.COSINE),
                )
            except Exception:
                return
        self._collection_ready = True

    def upsert_chunks(self, records: list[dict[str, Any]]) -> None:
        if not records:
            return

        vectors = [record["vector"] for record in records if record.get("vector")]
        if not vectors:
            return

        self.ensure_collection(len(vectors[0]))
        if not self._collection_ready:
            return
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[self._to_qdrant_point(record) for record in records],
            )
        except Exception:
            return

    def search(
        self,
        query_vector: list[float],
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if not query_vector:
            return []
        try:
            if not self.client.collection_exists(self.collection_name):
                return []
        except Exception:
            return []

        query_filter = None
        if filters:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = Filter(
                must=[
                    FieldCondition(key=key, match=MatchValue(value=value))
                    for key, value in filters.items()
                ]
            )

        try:
            if hasattr(self.client, "search"):
                return list(
                    self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=limit,
                        query_filter=query_filter,
                    )
                )
    
            query_response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                query_filter=query_filter,
            )
            return list(getattr(query_response, "points", []))
        except Exception:
            return []

    def delete_document(self, doc_id: int) -> None:
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue
        except ImportError:
            return

        try:
            if not self.client.collection_exists(self.collection_name):
                return
        except Exception:
            return

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                ),
            )
        except Exception:
            return

    def _to_qdrant_point(self, record: dict[str, Any]) -> dict[str, Any]:
        payload = dict(record.get("payload") or {})
        payload.setdefault("chunk_id", record["id"])
        return {
            "id": str(uuid5(NAMESPACE_URL, f"{self.collection_name}:{record['id']}")),
            "vector": record["vector"],
            "payload": payload,
        }


def build_default_vector_store() -> VectorStore:
    try:
        return QdrantVectorStore(url=settings.qdrant_url)
    except RuntimeError:
        return NoOpVectorStore()


__all__ = ["NoOpVectorStore", "QdrantVectorStore", "VectorStore", "build_default_vector_store"]
