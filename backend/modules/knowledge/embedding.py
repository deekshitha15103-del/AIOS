import json
import os
import urllib.request
from pathlib import Path

from backend.modules.knowledge.status import DocumentStatus


EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")

LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)
OPENAI_EMBEDDING_URL = os.getenv(
    "OPENAI_EMBEDDING_URL",
    "https://api.openai.com/v1/embeddings",
)

_model = None


def get_local_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(LOCAL_MODEL_NAME)

    return _model


def generate_local_embeddings(texts: list[str]) -> tuple[list[list[float]], str]:
    model = get_local_model()
    vectors = model.encode(texts).tolist()
    return vectors, LOCAL_MODEL_NAME


def generate_openai_embeddings(texts: list[str]) -> tuple[list[list[float]], str]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    payload = {
        "model": OPENAI_EMBEDDING_MODEL,
        "input": texts,
    }

    request = urllib.request.Request(
        OPENAI_EMBEDDING_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    vectors = [item["embedding"] for item in result["data"]]

    return vectors, OPENAI_EMBEDDING_MODEL


def generate_vectors(texts: list[str]) -> tuple[list[list[float]], str]:
    if EMBEDDING_PROVIDER == "openai":
        return generate_openai_embeddings(texts)

    return generate_local_embeddings(texts)


def generate_embeddings(document: dict) -> dict:
    chunks_path = Path(document["chunks_path"])
    document_dir = chunks_path.parent.parent

    embeddings_dir = document_dir / "embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    embeddings_path = embeddings_dir / "embeddings.json"

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    texts = [chunk["text"] for chunk in chunks]

    vectors, embedding_model = generate_vectors(texts)

    embedding_records = []

    for chunk, vector in zip(chunks, vectors):
        embedding_records.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "embedding_model": embedding_model,
                "vector": vector,
            }
        )

    embeddings_path.write_text(
        json.dumps(embedding_records, indent=2),
        encoding="utf-8",
    )

    document["status"] = DocumentStatus.EMBEDDED
    document["embeddings_path"] = str(embeddings_path)
    document["embedding_count"] = len(embedding_records)
    document["embedding_model"] = embedding_model

    return document