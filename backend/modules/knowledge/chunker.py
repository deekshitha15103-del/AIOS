import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.modules.knowledge.models import Chunk
from backend.modules.knowledge.status import DocumentStatus


MIN_CHUNK_CHARACTERS = 300
MAX_CHUNK_CHARACTERS = 1200


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

    for paragraph in paragraphs:
        if paragraph.startswith("--- Page") and paragraph.endswith("---"):
            continue

        if len(paragraph) > MAX_CHUNK_CHARACTERS:
            raw_chunks.extend(split_large_text(paragraph))
        else:
            raw_chunks.append(paragraph)

    raw_chunks = merge_small_chunks(raw_chunks)

    chunk_records = []
    created_at = datetime.now(timezone.utc)

    for index, chunk_text in enumerate(raw_chunks):
        chunk = Chunk(
            chunk_id=str(uuid4()),
            document_id=document["document_id"],
            chunk_index=index,
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