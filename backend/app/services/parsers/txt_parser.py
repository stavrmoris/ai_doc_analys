from __future__ import annotations

from pathlib import Path

from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument
from app.services.parsers.base import BaseParser


class TxtParser(BaseParser):
    def parse(self, path: Path) -> StructuredDocument:
        text = path.read_text(encoding="utf-8")
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]

        page_blocks = [
            DocumentBlock(
                type="paragraph",
                text=value,
                section_title=None,
            )
            for value in blocks
        ]

        return StructuredDocument(
            doc_id="local",
            pages=[DocumentPage(page_num=1, blocks=page_blocks)],
        )
