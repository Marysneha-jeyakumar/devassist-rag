from pathlib import Path
import hashlib
import re

import pymupdf

from app.core.logging import logger
from app.schemas.document import (
    DocumentMetadata,
    PageDocument,
)


class PDFLoader:
    """
    Loads PDF research papers and converts each readable
    page into a structured PageDocument object.
    """

    def load(
        self,
        file_path: str | Path,
    ) -> list[PageDocument]:

        path = Path(file_path)

        self._validate_file(path)

        logger.info(
            "Loading PDF: %s",
            path.name,
        )

        document_id = self._generate_document_id(path)

        documents: list[PageDocument] = []

        try:
            pdf = pymupdf.open(path)

            metadata = pdf.metadata or {}

            title = self._clean_metadata_value(
                metadata.get("title")
            )

            author = self._clean_metadata_value(
                metadata.get("author")
            )

            if not title:
                title = path.stem

            total_pages = len(pdf)

            logger.info(
                "PDF contains %s pages",
                total_pages,
            )

            for page_index, page in enumerate(pdf):

                raw_text = page.get_text("text")

                cleaned_text = self._normalize_text(
                    raw_text
                )

                if not cleaned_text:
                    continue

                page_metadata = DocumentMetadata(
                    document_id=document_id,
                    source=path.name,
                    file_name=path.name,
                    title=title,
                    author=author,
                    page_number=page_index + 1,
                    total_pages=total_pages,
                    file_type="pdf",
                )

                documents.append(
                    PageDocument(
                        text=cleaned_text,
                        metadata=page_metadata,
                    )
                )

            pdf.close()

            logger.info(
                "Extracted readable text from %s pages",
                len(documents),
            )

            return documents

        except pymupdf.FileDataError as exc:

            raise ValueError(
                f"Unable to read PDF file: {path.name}"
            ) from exc

    @staticmethod
    def _validate_file(
        path: Path,
    ) -> None:

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file was not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported."
            )

    @staticmethod
    def _generate_document_id(
        path: Path,
    ) -> str:

        sha256 = hashlib.sha256()

        with path.open("rb") as file:

            while chunk := file.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        text = text.replace(
            "\x00",
            "",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    @staticmethod
    def _clean_metadata_value(
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value if value else None