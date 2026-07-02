from fastapi import APIRouter, File, UploadFile

from backend.modules.knowledge.qa import answer_question
from backend.modules.knowledge.repository import list_documents
from backend.modules.knowledge.retrieval import search_document
from backend.modules.knowledge.schemas import (
    AskRequest,
    DocumentSearchRequest,
    KnowledgeStatus,
)
from backend.modules.knowledge.service import upload_document
from backend.schemas.common import APIResponse


router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/", response_model=APIResponse)
def knowledge_root():
    return APIResponse(
        success=True,
        message="Knowledge Engine is ready",
        data=KnowledgeStatus(
            module="knowledge",
            status="active",
        ),
    )


@router.post("/documents/upload", response_model=APIResponse)
async def upload_knowledge_document(file: UploadFile = File(...)):
    document = await upload_document(file)

    return APIResponse(
        success=True,
        message="Document uploaded successfully",
        data=document,
    )


@router.get("/documents", response_model=APIResponse)
def get_documents():
    documents = list_documents()

    return APIResponse(
        success=True,
        message="Documents fetched successfully",
        data=documents,
    )


@router.post("/search", response_model=APIResponse)
def search_knowledge(request: DocumentSearchRequest):
    document_dir = f"data/documents/{request.document_id}"

    results = search_document(
        document_dir=document_dir,
        query=request.query,
        top_k=request.top_k,
    )

    return APIResponse(
        success=True,
        message="Search completed successfully",
        data=results,
    )


@router.post("/ask", response_model=APIResponse)
def ask_knowledge(request: AskRequest):
    answer = answer_question(
        document_id=request.document_id,
        question=request.question,
        top_k=request.top_k,
    )

    return APIResponse(
        success=True,
        message="Answer generated successfully",
        data=answer,
    )