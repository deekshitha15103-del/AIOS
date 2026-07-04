import json
from pathlib import Path

import numpy as np

from backend.modules.knowledge.embedding import generate_vectors


def cosine_similarity(vector_a, vector_b):
    a = np.array(vector_a, dtype="float32")
    b = np.array(vector_b, dtype="float32")

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:
        return 0.0

    return float(np.dot(a, b) / (a_norm * b_norm))


def search_document(document_dir: str, query: str, top_k: int = 3):
    document_path = Path(document_dir)

    chunks_path = document_path / "chunks" / "chunks.json"
    embeddings_path = document_path / "embeddings" / "embeddings.json"

    if not chunks_path.exists():
        return []

    if not embeddings_path.exists():
        return []

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    embeddings = json.loads(embeddings_path.read_text(encoding="utf-8"))

    query_vectors, _ = generate_vectors([query])
    query_vector = query_vectors[0]

    chunk_map = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
    }

    results = []

    for embedding in embeddings:
        chunk_id = embedding["chunk_id"]
        chunk = chunk_map.get(chunk_id)

        if not chunk:
            continue

        score = cosine_similarity(query_vector, embedding["vector"])

        results.append(
            {
                "chunk_id": chunk_id,
                "document_id": embedding.get("document_id"),
                "score": score,
                "text": chunk.get("text", ""),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)

    return results[:top_k]