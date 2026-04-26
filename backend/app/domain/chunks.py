from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChunkingConfig:
    chunk_size: int = 800
    chunk_overlap: int = 120


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    page_num: int | None
    chunk_index: int
    section_title: str | None
    text: str
    metadata: dict[str, str | None] = field(default_factory=dict)


__all__ = ["ChunkRecord", "ChunkingConfig"]
