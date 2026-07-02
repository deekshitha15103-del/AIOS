import json
from pathlib import Path

import faiss
import numpy as np

from backend.modules.knowledge.embedding import _model


def search_document(document_dir: str, query: str, top_k: int = 3) -> list[dict]:
    document_path = Path(document_dir)

    index_path = document_path / "vectorstore" / "index.faiss"
    metadata_path = document_path / "vectorstore" / "metadata.json"
    chunks_path = document_path / "chunks" / "chunks.json"

    index = faiss.read_index(str(index_path))

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

    query_vector = _model.encode([query]).astype("float32")
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results = []

    for score, vector_index in zip(scores[0], indices[0]):
        meta = metadata[vector_index]
        chunk = chunks[vector_index]

        results.append(
            {
                "chunk_id": meta["chunk_id"],
                "document_id": meta["document_id"],
                "score": float(score),
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
            }
        )

    return results