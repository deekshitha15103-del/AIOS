import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.modules.knowledge.models import Chunk
from backend.modules.knowledge.status import DocumentStatus


MIN_CHUNK_CHARACTERS = 300
MAX_CHUNK_CHARACTERS = 1200

BAD_CHUNK_KEYWORDS = [
    "acknowledgements",
    "bibliography",
    "references",
    "contents",
    "rationalised 2023-24",
]


def is_low_quality_chunk(text: str) -> bool:
    lowered = text.lower().strip()

    if len(lowered) < 120:
        return True

    if any(keyword in lowered for keyword in BAD_CHUNK_KEYWORDS):
        return True

    if lowered.count("?") >= 2 and len(lowered.split()) < 120:
        return True

    if re.fullmatch(r"[\d\s\W]+", lowered):
        return True

    return False


def extract_page_number(text: str) -> int | None:
    match = re.search(r"===== PAGE (\d+) =====", text)
    if match:
        return int(match.group(1))
    return None


def remove_page_marker(text: str) -> str:
    return re.sub(r"===== PAGE \d+ =====", "", text).strip()


def split_large_text(text: str) -> list[str]:
    chunks = []
    remaining_text = text.strip()

    while len(remaining_text) > MAX_CHUNK_CHARACTERS:
        split_index = remaining_text.rfind(" ", 0, MAX_CHUNK_CHARACTERS)

        if split_index == -1:
            split_index = MAX_CHUNK_CHARACTERS

        chunks.append(remaining_text[:split_index].strip())
        remaining_text = remaining_text[split_index:].strip()

    if remaining_text:
        chunks.append(remaining_text)

    return chunks


def merge_small_chunks(chunks: list[str]) -> list[str]:
    merged_chunks = []
    buffer = ""

    for chunk in chunks:
        if not buffer:
            buffer = chunk
            continue

        combined = f"{buffer}\n\n{chunk}"

        if len(buffer) < MIN_CHUNK_CHARACTERS and len(combined) <= MAX_CHUNK_CHARACTERS:
            buffer = combined
        else:
            merged_chunks.append(buffer)
            buffer = chunk

    if buffer:
        merged_chunks.append(buffer)

    return merged_chunks


def create_chunks(document: dict) -> dict:
    text_path = Path(document["extracted_text_path"])
    document_dir = text_path.parent.parent

    chunks_dir = document_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = chunks_dir / "chunks.json"

    text = text_path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    raw_chunks = []
    current_page_number = None

    for paragraph in paragraphs:
        page_number = extract_page_number(paragraph)

        if page_number is not None:
            current_page_number = page_number
            paragraph = remove_page_marker(paragraph)

        if not paragraph:
            continue

        if len(paragraph) > MAX_CHUNK_CHARACTERS:
            for piece in split_large_text(paragraph):
                raw_chunks.append(
                    {
                        "text": piece,
                        "page_number": current_page_number,
                    }
                )
        else:
            raw_chunks.append(
                {
                    "text": paragraph,
                    "page_number": current_page_number,
                }
            )

    raw_text_chunks = [chunk["text"] for chunk in raw_chunks]
    merged_text_chunks = merge_small_chunks(raw_text_chunks)

    final_chunks = []
    for merged_text in merged_text_chunks:
        matched_page_number = None

        for original_chunk in raw_chunks:
            if original_chunk["text"] and original_chunk["text"] in merged_text:
                matched_page_number = original_chunk["page_number"]
                break

        if not is_low_quality_chunk(merged_text):
            final_chunks.append(
                {
                    "text": merged_text,
                    "page_number": matched_page_number,
                }
            )

    chunk_records = []
    created_at = datetime.now(timezone.utc)

    for index, chunk_data in enumerate(final_chunks):
        chunk_text = chunk_data["text"]

        chunk = Chunk(
            chunk_id=str(uuid4()),
            document_id=document["document_id"],
            chunk_index=index,
            page_number=chunk_data["page_number"],
            text=chunk_text,
            character_count=len(chunk_text),
            word_count=len(chunk_text.split()),
            created_at=created_at,
        )

        chunk_records.append(chunk.model_dump(mode="json"))

    chunks_path.write_text(
        json.dumps(chunk_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    document["status"] = DocumentStatus.CHUNKED
    document["chunks_path"] = str(chunks_path)
    document["chunk_count"] = len(chunk_records)

    return document