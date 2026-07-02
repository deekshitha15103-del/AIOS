from backend.modules.gateway.ollama_client import generate_answer
from backend.modules.knowledge.retrieval import search_document


def build_prompt(question: str, sources: list[dict]) -> str:
    context = "\n\n".join(
        [
            f"Source {index + 1}:\n{source['text']}"
            for index, source in enumerate(sources)
        ]
    )

    return f"""
You are AIOS, an enterprise document intelligence assistant.

Answer the user's question using only the context below.
Cite sources like [Source 1], [Source 2].
If the answer is not present in the context, say:
"I don't know based on the provided document."

Question:
{question}

Context:
{context}

Answer:
"""


def format_sources(sources: list[dict]) -> list[dict]:
    formatted_sources = []

    for index, source in enumerate(sources):
        formatted_sources.append(
            {
                "source_number": index + 1,
                "chunk_id": source["chunk_id"],
                "document_id": source["document_id"],
                "chunk_index": source["chunk_index"],
                "score": source["score"],
                "preview": source["text"][:300],
            }
        )

    return formatted_sources


def answer_question(document_id: str, question: str, top_k: int = 3) -> dict:
    sources = search_document(
        document_dir=f"data/documents/{document_id}",
        query=question,
        top_k=top_k,
    )

    prompt = build_prompt(question, sources)
    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": format_sources(sources),
    }