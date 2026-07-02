import json
from pathlib import Path

import faiss
import numpy as np

from backend.modules.knowledge.status import DocumentStatus


def build_faiss_index(document: dict) -> dict:
    embeddings_path = Path(document["embeddings_path"])
    document_dir = embeddings_path.parent.parent

    vector_dir = document_dir / "vectorstore"
    vector_dir.mkdir(parents=True, exist_ok=True)

    index_path = vector_dir / "index.faiss"
    metadata_path = vector_dir / "metadata.json"

    embedding_records = json.loads(embeddings_path.read_text(encoding="utf-8"))

    vectors = np.array(
        [record["vector"] for record in embedding_records],
        dtype="float32",
    )

    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(index, str(index_path))

    metadata = [
        {
            "chunk_id": record["chunk_id"],
            "document_id": record["document_id"],
            "embedding_model": record["embedding_model"],
            "vector_index": index_id,
        }
        for index_id, record in enumerate(embedding_records)
    ]

    metadata_path.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    document["status"] = DocumentStatus.INDEXED
    document["vector_index_path"] = str(index_path)
    document["vector_metadata_path"] = str(metadata_path)
    document["vector_count"] = len(metadata)

    return document