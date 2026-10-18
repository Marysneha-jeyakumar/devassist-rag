from app.core.logging import logger
from app.ingestion.section_detector import SectionDetector
from app.ingestion.text_cleaner import ScientificTextCleaner
from app.schemas.document import PageDocument
from app.schemas.section import (
    SectionDocument,
    SectionMetadata,
)


class PaperPreprocessor:

    def __init__(self) -> None:

        self.cleaner = ScientificTextCleaner()
        self.section_detector = SectionDetector()

    def process(
        self,
        pages: list[PageDocument],
    ) -> list[SectionDocument]:

        if not pages:
            return []

        sections: list[SectionDocument] = []

        first_page = pages[0]

        current_title = "Front Matter"
        current_type = "front_matter"

        current_text_parts: list[str] = []

        current_start_page = (
            first_page.metadata.page_number
        )

        current_end_page = current_start_page

        heading_detected = False

        section_index = 1

        def flush_current_section() -> None:
            nonlocal section_index
            nonlocal current_text_parts

            text = "\n\n".join(
                part
                for part in current_text_parts
                if part.strip()
            ).strip()

            if not text:
                current_text_parts = []
                return

            metadata = SectionMetadata(
                document_id=(
                    first_page.metadata.document_id
                ),
                source=(
                    first_page.metadata.source
                ),
                file_name=(
                    first_page.metadata.file_name
                ),
                title=(
                    first_page.metadata.title
                ),
                author=(
                    first_page.metadata.author
                ),
                section_index=section_index,
                section_title=current_title,
                section_type=current_type,
                page_start=current_start_page,
                page_end=current_end_page,
                heading_detected=heading_detected,
                file_type="pdf",
            )

            sections.append(
                SectionDocument(
                    text=text,
                    metadata=metadata,
                )
            )

            section_index += 1
            current_text_parts = []

        for page in pages:

            cleaned_text = self.cleaner.clean(
                page.text
            )

            if not cleaned_text:
                continue

            page_number = (
                page.metadata.page_number
            )

            segments = (
                self.section_detector.split_page(
                    cleaned_text
                )
            )

            for segment in segments:

                if segment.heading is not None:

                    # Finish previous section before
                    # starting the newly detected one.
                    flush_current_section()

                    current_title = (
                        segment.heading.title
                    )

                    current_type = (
                        segment.heading.section_type
                    )

                    current_start_page = page_number
                    current_end_page = page_number
                    heading_detected = True

                    if segment.text:
                        current_text_parts.append(
                            segment.text
                        )

                else:

                    # No new heading:
                    # this text belongs to the current
                    # section, possibly continuing from
                    # the previous page.
                    if segment.text:

                        current_text_parts.append(
                            segment.text
                        )

                        current_end_page = (
                            page_number
                        )

            # Section may continue throughout this page.
            if current_text_parts:
                current_end_page = page_number

        flush_current_section()

        logger.info(
            "Created %s scientific sections",
            len(sections),
        )

        return sections