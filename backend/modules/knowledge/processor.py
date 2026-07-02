from backend.core.logger import get_logger
from backend.modules.knowledge.ingestion import extract_pdf_text
from backend.modules.knowledge.repository import update_document_status
from backend.modules.knowledge.status import DocumentStatus


logger = get_logger(__name__)


class DocumentProcessor:
    def process(self, document: dict) -> dict:
        document_id = document["document_id"]

        logger.info(f"Starting processing for document: {document_id}")

        update_document_status(document_id, DocumentStatus.PROCESSING)
        document["status"] = DocumentStatus.PROCESSING

        document = extract_pdf_text(document)

        update_document_status(document_id, DocumentStatus.TEXT_EXTRACTED)

        logger.info(f"Text extracted for document: {document_id}")

        return document