from __future__ import annotations

from pathlib import Path

import fitz

from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument
from app.services.parsers.base import BaseParser


class PdfParser(BaseParser):
    def parse(self, path: Path) -> StructuredDocument:
        pages: list[DocumentPage] = []

        pdf = fitz.open(path)
        try:
            for page_num, page in enumerate(pdf, start=1):
                blocks = []
                for block in page.get_text("blocks"):
                    text = block[4].strip()
                    if not text:
                        continue
                    blocks.append(
                        DocumentBlock(
                            type="paragraph",
                            text=text,
                            section_title=None,
                        )
                    )
                pages.append(DocumentPage(page_num=page_num, blocks=blocks))
        finally:
            pdf.close()

        return StructuredDocument(doc_id="local", pages=pages)
