from dataclasses import dataclass, field


@dataclass
class DocumentBlock:
    type: str
    text: str
    section_title: str | None = None


@dataclass
class DocumentPage:
    page_num: int
    blocks: list[DocumentBlock] = field(default_factory=list)


@dataclass
class StructuredDocument:
    doc_id: str
    pages: list[DocumentPage] = field(default_factory=list)


__all__ = ["DocumentBlock", "DocumentPage", "StructuredDocument"]
