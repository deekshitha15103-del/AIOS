from fastapi import UploadFile

from backend.core.exceptions import AIOSException


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
}

# 50 MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


async def validate_upload_file(file: UploadFile) -> bytes:
    """
    Validates an uploaded document before it enters the Knowledge Engine.

    Current Version (v0.1):
    - Accepts PDF files only
    - Maximum file size: 50 MB
    """

    content = await file.read()

    if not file.filename:
        raise AIOSException(
            message="Filename is required",
            status_code=400,
        )

    is_pdf_content_type = file.content_type in ALLOWED_CONTENT_TYPES
    is_pdf_extension = file.filename.lower().endswith(".pdf")

    if not is_pdf_content_type and not is_pdf_extension:
        raise AIOSException(
            message="Only PDF files are supported for now",
            status_code=400,
        )

    if len(content) == 0:
        raise AIOSException(
            message="Uploaded file is empty",
            status_code=400,
        )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise AIOSException(
            message="File size exceeds the 50 MB limit",
            status_code=400,
        )

    return content