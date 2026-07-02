from pathlib import Path
from uuid import uuid4


DOCUMENTS_DIR = Path("data/documents")


def save_uploaded_file(filename: str, content: bytes) -> dict:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid4())
    document_dir = DOCUMENTS_DIR / document_id
    document_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = filename.replace(" ", "_")
    file_path = document_dir / safe_filename

    file_path.write_bytes(content)

    return {
        "document_id": document_id,
        "filename": filename,
        "stored_filename": safe_filename,
        "file_path": str(file_path),
    }