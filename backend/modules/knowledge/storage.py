from pathlib import Path
from uuid import uuid4


UPLOAD_DIR = Path("data/uploads")


def save_uploaded_file(filename: str, content: bytes) -> dict:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid4())
    safe_filename = filename.replace(" ", "_")
    stored_filename = f"{document_id}_{safe_filename}"
    file_path = UPLOAD_DIR / stored_filename

    file_path.write_bytes(content)

    return {
        "document_id": document_id,
        "filename": filename,
        "stored_filename": stored_filename,
        "file_path": str(file_path),
    }