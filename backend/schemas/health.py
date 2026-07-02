from pydantic import BaseModel


class RootResponse(BaseModel):
    name: str
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str