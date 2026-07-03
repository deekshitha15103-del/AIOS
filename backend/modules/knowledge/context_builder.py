from typing import List


def build_context(chunks: List[dict]) -> str:
    """
    Builds a clean context string from retrieved chunks.
    """

    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        page = chunk.get("page_number")

        header = f"[Source {i}]"

        if page is not None:
            header += f" (Page {page})"

        context_parts.append(
            f"""{header}

{chunk["text"]}
"""
        )

    return "\n\n".join(context_parts)