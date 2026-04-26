from pathlib import Path

import fitz

from app.services.parsers.pdf_parser import PdfParser
from app.services.parsers.txt_parser import TxtParser


def sample_pdf_path(tmp_path: Path) -> Path:
    path = tmp_path / "sample.pdf"
    document = fitz.open()
    page_one = document.new_page()
    page_one.insert_text((72, 72), "Agreement")
    page_one.insert_text((72, 200), "First clause")
    page_two = document.new_page()
    page_two.insert_text((72, 72), "Second page text")
    document.save(path)
    document.close()
    return path


def test_txt_parser_returns_single_page_structure(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("Intro text\n\nThis is the body.\n\nAnd another paragraph.", encoding="utf-8")

    result = TxtParser().parse(path)

    assert result.doc_id == "local"
    assert len(result.pages) == 1
    assert [block.text for block in result.pages[0].blocks] == [
        "Intro text",
        "This is the body.",
        "And another paragraph.",
    ]
    assert all(block.type == "paragraph" for block in result.pages[0].blocks)
    assert all(block.section_title is None for block in result.pages[0].blocks)


def test_pdf_parser_extracts_text_from_text_pdf(tmp_path: Path) -> None:
    result = PdfParser().parse(sample_pdf_path(tmp_path))

    assert len(result.pages) == 2
    assert [page.page_num for page in result.pages] == [1, 2]
    assert [block.text for block in result.pages[0].blocks] == ["Agreement", "First clause"]
    assert [block.text for block in result.pages[1].blocks] == ["Second page text"]
    assert all(block.type == "paragraph" for page in result.pages for block in page.blocks)
