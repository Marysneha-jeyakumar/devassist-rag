from collections import Counter
from pathlib import Path
from statistics import mean
import json

from app.ingestion.chunker import (
    ScientificPaperChunker,
)
from app.ingestion.paper_preprocessor import (
    PaperPreprocessor,
)
from app.ingestion.pdf_loader import PDFLoader


PDF_PATH = Path(
    "data/raw/flood_prediction_sample.pdf"
)


def main() -> None:

    loader = PDFLoader()

    pages = loader.load(
        PDF_PATH
    )

    preprocessor = PaperPreprocessor()

    sections = preprocessor.process(
        pages
    )

    chunker = ScientificPaperChunker()

    chunks = chunker.chunk_sections(
        sections
    )

    print("\n")
    print("=" * 70)
    print("SCIENTIFIC CHUNKING RESULT")
    print("=" * 70)

    print(
        f"Pages: {len(pages)}"
    )

    print(
        f"Sections: {len(sections)}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    if not chunks:
        print("No chunks generated.")
        return

    token_counts = [
        chunk.metadata.token_count
        for chunk in chunks
    ]

    print("\nTOKEN STATISTICS")

    print(
        f"Minimum: {min(token_counts)}"
    )

    print(
        f"Maximum: {max(token_counts)}"
    )

    print(
        f"Average: {mean(token_counts):.2f}"
    )

    section_counts = Counter(
        chunk.metadata.section_type
        for chunk in chunks
    )

    print("\nCHUNKS BY SECTION")

    for section_type, count in (
        section_counts.items()
    ):

        print(
            f"{section_type}: {count}"
        )

    print("\n")
    print("=" * 70)
    print("SAMPLE CHUNKS")
    print("=" * 70)

    for chunk in chunks[:5]:

        metadata = chunk.metadata

        print(
            f"\nChunk "
            f"{metadata.chunk_index}/"
            f"{metadata.total_chunks}"
        )

        print(
            f"Section: "
            f"{metadata.section_title}"
        )

        print(
            f"Type: "
            f"{metadata.section_type}"
        )

        print(
            f"Pages: "
            f"{metadata.page_start}"
            f"-"
            f"{metadata.page_end}"
        )

        print(
            f"Tokens: "
            f"{metadata.token_count}"
        )

        print(
            f"Chunk ID: "
            f"{metadata.chunk_id[:15]}..."
        )

        print("\nPreview:")

        print(
            chunk.text[:500]
            .replace("\n", " ")
        )

        print(
            "\n" + "-" * 70
        )

    output_directory = Path(
        "data/processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / "paper_chunks.json"
    )

    output_data = [
        chunk.model_dump()
        for chunk in chunks
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nSaved chunks to:"
    )

    print(
        output_path
    )


if __name__ == "__main__":
    main()