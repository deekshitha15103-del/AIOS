from backend.modules.gateway.ollama_client import (
    generate_answer,
    generate_stream,
)
from backend.modules.knowledge.memory import add_message, get_history
from backend.modules.knowledge.multiretrieval import search_all_documents
from backend.modules.knowledge.response_cleaner import clean_answer
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
            f"[Source {i + 1}]\n{source['text']}"
            for i, source in enumerate(sources)
        ]
    )

    return f"""
You are AIOS, an enterprise document intelligence assistant.

Use ONLY the retrieved context to answer the question.
Use conversation history only to understand follow-up questions.

Rules:
1. If the context contains relevant information, answer clearly.
2. Cite sources like [Source 1], [Source 2].
3. Do not add "I don't know" after giving an answer.
4. If none of the retrieved sources contain relevant information, say exactly:
"I don't know based on the uploaded documents."
5. Never invent facts.

Conversation History:
{history_text}

Retrieved Context:
{context}

Question:
{question}

Answer:
"""


def format_sources(sources: list[dict]) -> list[dict]:
    formatted = []

    for i, source in enumerate(sources):
        formatted.append(
            {
                "source_number": i + 1,
                "chunk_id": source["chunk_id"],
                "document_id": source["document_id"],
                "chunk_index": source["chunk_index"],
                "page_number": source.get("page_number"),
                "score": source["score"],
                "semantic_score": source.get("semantic_score"),
                "keyword_score": source.get("keyword_score"),
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
    answer = clean_answer(answer)

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

    full_answer = clean_answer(full_answer)

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
    answer = clean_answer(answer)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "sources": format_sources(sources),
    }