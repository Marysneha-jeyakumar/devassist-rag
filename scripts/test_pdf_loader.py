from pathlib import Path

from app.ingestion.pdf_loader import PDFLoader


def main():

    pdf_path = Path(
        "data/raw/flood_prediction_sample.pdf"
    )

    loader = PDFLoader()

    documents = loader.load(pdf_path)

    print("\nPDF INGESTION RESULT")
    print("=" * 60)

    print(f"Pages extracted: {len(documents)}")

    if not documents:
        print("No readable text was extracted.")
        return

    first_document = documents[0]

    print(
        f"Document ID: "
        f"{first_document.metadata.document_id[:16]}..."
    )

    print(
        f"Title: "
        f"{first_document.metadata.title}"
    )

    print(
        f"Author: "
        f"{first_document.metadata.author}"
    )

    print(
        f"Total pages: "
        f"{first_document.metadata.total_pages}"
    )

    print(
        f"Current page: "
        f"{first_document.metadata.page_number}"
    )

    print(
        f"Source: "
        f"{first_document.metadata.source}"
    )

    print("\nTEXT PREVIEW")
    print("=" * 60)

    print(first_document.text[:1000])
    print(
    first_document.model_dump()
)
    
if __name__ == "__main__":
    main()

