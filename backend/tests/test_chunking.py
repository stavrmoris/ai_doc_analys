from app.domain.chunks import ChunkingConfig
from app.domain.documents import DocumentBlock, DocumentPage, StructuredDocument
from app.services.chunking import ChunkingService


def test_chunking_preserves_metadata_across_multiple_chunks() -> None:
    document = StructuredDocument(
        doc_id="doc-123",
        pages=[
            DocumentPage(
                page_num=7,
                blocks=[
                    DocumentBlock(
                        type="paragraph",
                        text="abcdefghijklmnopqrstuvwxyz" * 10,
                        section_title="Introduction",
                    )
                ],
            )
        ],
    )

    service = ChunkingService(ChunkingConfig(chunk_size=100, chunk_overlap=20))
    chunks = service.chunk_document(document)

    assert len(chunks) == 3
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert all(chunk.doc_id == "doc-123" for chunk in chunks)
    assert all(chunk.page_num == 7 for chunk in chunks)
    assert all(chunk.section_title == "Introduction" for chunk in chunks)
    assert all(chunk.metadata["doc_id"] == "doc-123" for chunk in chunks)
    assert all(chunk.metadata["page_num"] == "7" for chunk in chunks)
    assert [chunk.metadata["chunk_index"] for chunk in chunks] == ["0", "1", "2"]
    assert all(chunk.metadata["section_title"] == "Introduction" for chunk in chunks)
    assert all(chunk.text for chunk in chunks)


def test_chunking_preserves_exact_overlap_without_trimming_boundaries() -> None:
    document = StructuredDocument(
        doc_id="doc-overlap",
        pages=[
            DocumentPage(
                page_num=1,
                blocks=[
                    DocumentBlock(
                        type="paragraph",
                        text="abcdefghij",
                        section_title=None,
                    )
                ],
            )
        ],
    )

    service = ChunkingService(ChunkingConfig(chunk_size=6, chunk_overlap=2))
    chunks = service.chunk_document(document)

    assert [chunk.text for chunk in chunks] == ["abcdef", "efghij"]
    assert [chunk.metadata["chunk_index"] for chunk in chunks] == ["0", "1"]
    assert all(chunk.section_title is None for chunk in chunks)
    assert all(chunk.metadata["section_title"] is None for chunk in chunks)
