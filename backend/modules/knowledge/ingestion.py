from pathlib import Path
import re

from pypdf import PdfReader

from backend.modules.knowledge.status import DocumentStatus


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text before chunking.
    """

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove repeated page markers
    text = re.sub(r"--- Page \d+ ---", "", text)

    # Remove common footer/header noise
    garbage_patterns = [
        "Rationalised 2023-24",
        "ACKNOWLEDGEMENTS",
        "Contents",
        "Bibliography",
        "References",
        "Index",
    ]

    for pattern in garbage_patterns:
        text = text.replace(pattern, "")

    return text.strip()


def extract_pdf_text(document: dict) -> dict:
    file_path = Path(document["file_path"])
    document_dir = file_path.parent

    extracted_dir = document_dir / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)

    output_path = extracted_dir / "text.txt"

    reader = PdfReader(str(file_path))

    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        text = clean_text(text)

        # Skip empty pages
        if len(text) < 50:
            continue

        pages_text.append(
            f"\n\n===== PAGE {page_number} =====\n\n{text}"
        )

    full_text = "\n".join(pages_text)

    output_path.write_text(full_text, encoding="utf-8")

    document["status"] = DocumentStatus.TEXT_EXTRACTED
    document["extracted_text_path"] = str(output_path)
    document["page_count"] = len(reader.pages)

    return document