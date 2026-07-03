import json
import re
from pathlib import Path

import faiss
from rank_bm25 import BM25Okapi

from backend.modules.knowledge.embedding import _model


SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0 for _ in scores]

    return [
        (score - min_score) / (max_score - min_score)
        for score in scores
    ]


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

    semantic_scores, semantic_indices = index.search(
        query_vector,
        min(top_k * 3, len(chunks)),
    )

    tokenized_chunks = [tokenize(chunk["text"]) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)

    keyword_scores = bm25.get_scores(tokenize(query)).tolist()
    normalized_keyword_scores = normalize_scores(keyword_scores)

    results_by_index = {}

    for semantic_score, vector_index in zip(semantic_scores[0], semantic_indices[0]):
        if vector_index == -1:
            continue

        results_by_index[vector_index] = {
            "semantic_score": float(semantic_score),
            "keyword_score": normalized_keyword_scores[vector_index],
        }

    for index_id, keyword_score in enumerate(normalized_keyword_scores):
        if keyword_score > 0:
            if index_id not in results_by_index:
                results_by_index[index_id] = {
                    "semantic_score": 0.0,
                    "keyword_score": keyword_score,
                }

    ranked_results = []

    for index_id, scores in results_by_index.items():
        chunk = chunks[index_id]
        meta = metadata[index_id]

        final_score = (
            SEMANTIC_WEIGHT * scores["semantic_score"]
            + KEYWORD_WEIGHT * scores["keyword_score"]
        )

        ranked_results.append(
            {
                "chunk_id": meta["chunk_id"],
                "document_id": meta["document_id"],
                "score": float(final_score),
                "semantic_score": scores["semantic_score"],
                "keyword_score": scores["keyword_score"],
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
                "page_number": chunk.get("page_number"),
            }
        )

    ranked_results.sort(key=lambda item: item["score"], reverse=True)

    return ranked_results[:top_k]