from datetime import datetime
from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int

    page_number: int | None = None
    section: str | None = None

    text: str

    character_count: int
    word_count: int

    embedding_status: str = "pending"

    created_at: datetime

    version: int = 1