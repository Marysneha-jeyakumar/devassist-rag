from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str

    source: str
    file_name: str

    title: str | None = None
    author: str | None = None

    page_number: int = Field(ge=1)
    total_pages: int = Field(ge=1)

    file_type: str = "pdf"


class PageDocument(BaseModel):
    text: str
    metadata: DocumentMetadata