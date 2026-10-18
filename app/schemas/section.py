from pydantic import BaseModel, Field


class SectionMetadata(BaseModel):
    document_id: str

    source: str
    file_name: str

    title: str | None = None
    author: str | None = None

    section_index: int = Field(ge=1)

    section_title: str
    section_type: str

    page_start: int = Field(ge=1)
    page_end: int = Field(ge=1)

    heading_detected: bool

    file_type: str = "pdf"


class SectionDocument(BaseModel):
    text: str = Field(min_length=1)

    metadata: SectionMetadata