from pathlib import Path

from pypdf import PdfReader

from backend.modules.knowledge.status import DocumentStatus


def extract_pdf_text(document: dict) -> dict:
    file_path = Path(document["file_path"])
    document_dir = file_path.parent

    extracted_dir = document_dir / "extracted"
    extracted_dir.mkdir(parents=True, exist_ok=True)

    output_path = extracted_dir / "text.txt"

    reader = PdfReader(str(file_path))

    pages_text: list[str] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages_text.append(f"\n\n--- Page {page_number} ---\n\n{text}")

    full_text = "".join(pages_text)
    output_path.write_text(full_text, encoding="utf-8")

    document["status"] = DocumentStatus.TEXT_EXTRACTED
    document["extracted_text_path"] = str(output_path)
    document["page_count"] = len(reader.pages)

    return document