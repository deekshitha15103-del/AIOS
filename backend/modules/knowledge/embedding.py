import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from backend.modules.knowledge.status import DocumentStatus


MODEL_NAME = "all-MiniLM-L6-v2"

_model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(document: dict) -> dict:
    chunks_path = Path(document["chunks_path"])
    document_dir = chunks_path.parent.parent

    embeddings_dir = document_dir / "embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    embeddings_path = embeddings_dir / "embeddings.json"

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    texts = [chunk["text"] for chunk in chunks]

    vectors = _model.encode(texts).tolist()

    embedding_records = []

    for chunk, vector in zip(chunks, vectors):
        embedding_records.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "embedding_model": MODEL_NAME,
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
    document["embedding_model"] = MODEL_NAME

    return document