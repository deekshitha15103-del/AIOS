from backend.modules.gateway.ollama_client import generate_answer
from backend.modules.knowledge.retrieval import search_document


def answer_question(document_id: str, question: str, top_k: int = 3) -> dict:
    document_dir = f"data/documents/{document_id}"

    sources = search_document(
        document_dir=document_dir,
        query=question,
        top_k=top_k,
    )

    context = "\n\n".join(
        [
            f"Source {index + 1}:\n{source['text']}"
            for index, source in enumerate(sources)
        ]
    )

    prompt = f"""
You are AIOS, an enterprise document intelligence assistant.

Answer the user's question using only the context below.
If the answer is not present in the context, say: "I don't know based on the provided document."

Question:
{question}

Context:
{context}

Answer:
"""

    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }