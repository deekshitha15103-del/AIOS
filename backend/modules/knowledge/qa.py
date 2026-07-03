from backend.modules.gateway.ollama_client import (
    generate_answer,
    generate_stream,
)
from backend.modules.knowledge.memory import add_message, get_history
from backend.modules.knowledge.multiretrieval import search_all_documents
from backend.modules.knowledge.retrieval import search_document


def build_history(history: list[dict]) -> str:
    if not history:
        return "No previous conversation."

    return "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history
    )


def build_prompt(question: str, sources: list[dict], history: list[dict]) -> str:
    history_text = build_history(history)

    context = "\n\n".join(
        [
            f"Source {i + 1}\n{source['text']}"
            for i, source in enumerate(sources)
        ]
    )

    return f"""
You are AIOS, an Enterprise AI Assistant.

Use ONLY the retrieved context to answer.

If the answer cannot be found in the context, say:

"I don't know based on the uploaded documents."

Always cite the source using:

[Source 1]
[Source 2]

Conversation History:

{history_text}

Question:

{question}

Retrieved Context:

{context}

Answer:
"""


def format_sources(sources):
    formatted = []

    for i, source in enumerate(sources):
        formatted.append(
            {
                "source_number": i + 1,
                "chunk_id": source["chunk_id"],
                "document_id": source["document_id"],
                "chunk_index": source["chunk_index"],
                "score": source["score"],
                "preview": source["text"][:300],
            }
        )

    return formatted


def answer_question(
    session_id: str,
    document_id: str,
    question: str,
    top_k: int = 3,
):
    history = get_history(session_id)

    sources = search_document(
        document_dir=f"data/documents/{document_id}",
        query=question,
        top_k=top_k,
    )

    prompt = build_prompt(question, sources, history)

    answer = generate_answer(prompt)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources": format_sources(sources),
    }


def stream_answer_question(
    session_id: str,
    document_id: str,
    question: str,
    top_k: int = 3,
):
    history = get_history(session_id)

    sources = search_document(
        document_dir=f"data/documents/{document_id}",
        query=question,
        top_k=top_k,
    )

    prompt = build_prompt(question, sources, history)

    full_answer = ""

    for token in generate_stream(prompt):
        full_answer += token
        yield token

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", full_answer)


def answer_all_documents(
    session_id: str,
    question: str,
    top_k: int = 5,
):
    history = get_history(session_id)

    sources = search_all_documents(
        query=question,
        top_k=top_k,
    )

    prompt = build_prompt(question, sources, history)

    answer = generate_answer(prompt)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources": format_sources(sources),
    }