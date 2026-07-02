from datetime import datetime, timezone

from backend.core.database import get_connection
from backend.modules.knowledge.status import DocumentStatus


def register_document(document: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()

    document_record = {
        **document,
        "status": DocumentStatus.UPLOADED,
        "created_at": now,
    }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            id,
            filename,
            stored_filename,
            file_path,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            document_record["document_id"],
            document_record["filename"],
            document_record["stored_filename"],
            document_record["file_path"],
            document_record["status"],
            document_record["created_at"],
        ),
    )

    connection.commit()
    connection.close()

    return document_record


def list_documents() -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            filename,
            stored_filename,
            file_path,
            status,
            created_at
        FROM documents
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def update_document_status(document_id: str, status: str) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            document_id,
        ),
    )

    connection.commit()
    connection.close()