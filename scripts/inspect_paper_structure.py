from pathlib import Path
import json

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

    print("\n")
    print("=" * 70)
    print("SCIENTIFIC PAPER STRUCTURE")
    print("=" * 70)

    print(
        f"Pages extracted: {len(pages)}"
    )

    print(
        f"Sections created: {len(sections)}"
    )

    print("\nDetected sections:")

    for section in sections:

        metadata = section.metadata

        print(
            f"\n[{metadata.section_index}] "
            f"{metadata.section_title}"
        )

        print(
            f"Type: {metadata.section_type}"
        )

        print(
            f"Pages: "
            f"{metadata.page_start}"
            f"-"
            f"{metadata.page_end}"
        )

        print(
            f"Characters: {len(section.text)}"
        )

        print(
            "Preview:"
        )

        print(
            section.text[:250]
            .replace("\n", " ")
        )

    # -------------------------
    # Simple quality statistics
    # -------------------------

    total_characters = sum(
        len(section.text)
        for section in sections
    )

    recognized_characters = sum(
        len(section.text)
        for section in sections
        if section.metadata.heading_detected
    )

    if total_characters:

        recognition_coverage = (
            recognized_characters
            / total_characters
            * 100
        )

    else:

        recognition_coverage = 0

    print("\n")
    print("=" * 70)
    print("STRUCTURE QUALITY")
    print("=" * 70)

    print(
        f"Total characters: "
        f"{total_characters}"
    )

    print(
        f"Recognized section coverage: "
        f"{recognition_coverage:.2f}%"
    )

    # -------------------------
    # Save inspection JSON
    # -------------------------

    output_directory = Path(
        "data/processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / "paper_sections.json"
    )

    output_data = [
        section.model_dump()
        for section in sections
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
        f"\nSaved processed output to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()