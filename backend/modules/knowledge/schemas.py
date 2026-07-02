from pydantic import BaseModel


class KnowledgeStatus(BaseModel):
    module: str
    status: str


class DocumentSearchRequest(BaseModel):
    document_dir: str
    query: str
    top_k: int = 3