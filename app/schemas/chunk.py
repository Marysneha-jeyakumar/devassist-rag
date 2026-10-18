from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):

    chunk_id: str

    document_id: str

    source: str
    file_name: str

    paper_title: str | None = None
    author: str | None = None

    section_index: int = Field(ge=1)

    section_title: str
    section_type: str

    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)

    chunk_index: int = Field(ge=1)
    total_chunks: int = Field(ge=1)

    token_count: int = Field(ge=1)

    file_type: str = "pdf"


class ChunkDocument(BaseModel):

    text: str = Field(min_length=1)

    metadata: ChunkMetadata