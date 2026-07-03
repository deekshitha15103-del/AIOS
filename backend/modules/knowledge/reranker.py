from sentence_transformers import CrossEncoder


RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_reranker = CrossEncoder(RERANKER_MODEL_NAME)


def rerank_results(query: str, results: list[dict], top_k: int = 3) -> list[dict]:
    if not results:
        return []

    pairs = [(query, result["text"]) for result in results]

    rerank_scores = _reranker.predict(pairs)

    reranked = []

    for result, score in zip(results, rerank_scores):
        updated = result.copy()
        updated["rerank_score"] = float(score)
        reranked.append(updated)

    reranked.sort(key=lambda item: item["rerank_score"], reverse=True)

    return reranked[:top_k]