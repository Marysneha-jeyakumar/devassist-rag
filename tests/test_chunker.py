from app.ingestion.chunker import (
    ScientificPaperChunker,
)
from app.schemas.section import (
    SectionDocument,
    SectionMetadata,
)


def create_section(
    text: str,
    section_type: str = "methodology",
) -> SectionDocument:

    return SectionDocument(
        text=text,
        metadata=SectionMetadata(
            document_id="test-document",
            source="test.pdf",
            file_name="test.pdf",
            title="Test Paper",
            author="Test Author",
            section_index=1,
            section_title="Methodology",
            section_type=section_type,
            page_start=2,
            page_end=4,
            heading_detected=True,
            file_type="pdf",
        ),
    )


def test_chunk_does_not_exceed_limit():

    text = "Flood prediction model. " * 1000

    section = create_section(text)

    chunker = ScientificPaperChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_sections(
        [section]
    )

    assert len(chunks) > 1

    for chunk in chunks:

        assert (
            chunk.metadata.token_count
            <= 100
        )


def test_metadata_is_preserved():

    section = create_section(
        "Flood prediction using rainfall data."
    )

    chunker = ScientificPaperChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_sections(
        [section]
    )

    first_chunk = chunks[0]

    assert (
        first_chunk.metadata.source
        == "test.pdf"
    )

    assert (
        first_chunk.metadata.section_type
        == "methodology"
    )

    assert (
        first_chunk.metadata.page_start
        == 2
    )


def test_references_are_skipped():

    reference_section = create_section(
        "Smith et al. 2024...",
        section_type="references",
    )

    chunker = ScientificPaperChunker()

    chunks = chunker.chunk_sections(
        [reference_section]
    )

    assert chunks == []