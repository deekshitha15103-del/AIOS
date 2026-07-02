from fastapi import UploadFile

from backend.modules.knowledge.processor import DocumentProcessor
from backend.modules.knowledge.repository import register_document
from backend.modules.knowledge.storage import save_uploaded_file
from backend.modules.knowledge.validator import validate_upload_file


processor = DocumentProcessor()


async def upload_document(file: UploadFile) -> dict:
    content = await validate_upload_file(file)

    stored_document = save_uploaded_file(
        filename=file.filename,
        content=content,
    )

    document = register_document(stored_document)

    document = processor.process(document)

    return document