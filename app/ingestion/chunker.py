import hashlib

import tiktoken

from app.core.config import get_settings
from app.core.logging import logger
from app.schemas.chunk import (
    ChunkDocument,
    ChunkMetadata,
)
from app.schemas.section import SectionDocument


class ScientificPaperChunker:

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:

        settings = get_settings()

        self.chunk_size = (
            chunk_size
            or settings.CHUNK_SIZE_TOKENS
        )

        self.chunk_overlap = (
            chunk_overlap
            if chunk_overlap is not None
            else settings.CHUNK_OVERLAP_TOKENS
        )

        if self.chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if self.chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller "
                "than chunk_size."
            )

        self.encoding = tiktoken.get_encoding(
            "cl100k_base"
        )

        # These sections normally add little value
        # to semantic retrieval.
        self.excluded_section_types = {
            "references",
            "acknowledgements",
        }

    def chunk_sections(
        self,
        sections: list[SectionDocument],
    ) -> list[ChunkDocument]:

        all_chunks: list[ChunkDocument] = []

        for section in sections:

            if (
                section.metadata.section_type
                in self.excluded_section_types
            ):
                logger.info(
                    "Skipping section: %s",
                    section.metadata.section_title,
                )

                continue

            section_chunks = (
                self._chunk_single_section(
                    section
                )
            )

            all_chunks.extend(
                section_chunks
            )

        logger.info(
            "Created %s chunks from %s sections",
            len(all_chunks),
            len(sections),
        )

        return all_chunks

    def _chunk_single_section(
        self,
        section: SectionDocument,
    ) -> list[ChunkDocument]:

        token_ids = self.encoding.encode(
            section.text
        )

        if not token_ids:
            return []

        step_size = (
            self.chunk_size
            - self.chunk_overlap
        )

        token_windows: list[list[int]] = []

        start = 0

        while start < len(token_ids):

            end = min(
                start + self.chunk_size,
                len(token_ids),
            )

            token_windows.append(
                token_ids[start:end]
            )

            if end >= len(token_ids):
                break

            start += step_size

        total_chunks = len(token_windows)

        chunks: list[ChunkDocument] = []

        for index, window in enumerate(
            token_windows,
            start=1,
        ):

            text = self.encoding.decode(
                window
            ).strip()

            if not text:
                continue

            chunk_id = self._generate_chunk_id(
                document_id=(
                    section.metadata.document_id
                ),
                section_index=(
                    section.metadata.section_index
                ),
                chunk_index=index,
                text=text,
            )

            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                document_id=(
                    section.metadata.document_id
                ),
                source=(
                    section.metadata.source
                ),
                file_name=(
                    section.metadata.file_name
                ),
                paper_title=(
                    section.metadata.title
                ),
                author=(
                    section.metadata.author
                ),
                section_index=(
                    section.metadata.section_index
                ),
                section_title=(
                    section.metadata.section_title
                ),
                section_type=(
                    section.metadata.section_type
                ),
                page_start=(
                    section.metadata.page_start
                ),
                page_end=(
                    section.metadata.page_end
                ),
                chunk_index=index,
                total_chunks=total_chunks,
                token_count=len(window),
                file_type=(
                    section.metadata.file_type
                ),
            )

            chunks.append(
                ChunkDocument(
                    text=text,
                    metadata=metadata,
                )
            )

        return chunks

    @staticmethod
    def _generate_chunk_id(
        document_id: str,
        section_index: int,
        chunk_index: int,
        text: str,
    ) -> str:

        raw_value = (
            f"{document_id}:"
            f"{section_index}:"
            f"{chunk_index}:"
            f"{text}"
        )

        return hashlib.sha256(
            raw_value.encode("utf-8")
        ).hexdigest()