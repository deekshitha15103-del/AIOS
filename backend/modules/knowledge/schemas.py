from pydantic import BaseModel


class KnowledgeStatus(BaseModel):
    module: str
    status: str


class DocumentSearchRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 3


class AskRequest(BaseModel):
    document_id: str
    question: str
    top_k: int = 3