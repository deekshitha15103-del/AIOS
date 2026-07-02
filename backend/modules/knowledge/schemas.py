from pydantic import BaseModel


class KnowledgeStatus(BaseModel):
    module: str
    status: str