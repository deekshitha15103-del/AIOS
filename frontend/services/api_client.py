import requests


API_BASE_URL = "http://127.0.0.1:8000/api/v1"


def upload_document(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/knowledge/documents/upload",
        files=files,
        timeout=600,
    )

    return response


def ask_document(session_id: str, document_id: str, question: str, top_k: int = 3):
    payload = {
        "session_id": session_id,
        "document_id": document_id,
        "question": question,
        "top_k": top_k,
    }

    response = requests.post(
        f"{API_BASE_URL}/knowledge/ask",
        json=payload,
        timeout=600,
    )

    return response