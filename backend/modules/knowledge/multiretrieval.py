import json
from pathlib import Path

import faiss
import numpy as np

from backend.modules.knowledge.embedding import _model


DOCUMENTS_DIR = Path("data/documents")


def search_all_documents(query: str, top_k: int = 5):
    query_vector = _model.encode([query]).astype("float32")
    faiss.normalize_L2(query_vector)

    all_results = []

    if not DOCUMENTS_DIR.exists():
        return []

    for document_dir in DOCUMENTS_DIR.iterdir():

        if not document_dir.is_dir():
            continue

        index_path = document_dir / "vectorstore" / "index.faiss"
        metadata_path = document_dir / "vectorstore" / "metadata.json"
        chunks_path = document_dir / "chunks" / "chunks.json"

        if not (
            index_path.exists()
            and metadata_path.exists()
            and chunks_path.exists()
        ):
            continue

        index = faiss.read_index(str(index_path))

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))

        scores, indices = index.search(query_vector, top_k)

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            chunk = chunks[idx]

            all_results.append(
                {
                    "document_id": chunk["document_id"],
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk["chunk_index"],
                    "score": float(score),
                    "text": chunk["text"],
                }
            )

    all_results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return all_results[:top_k]