import json
from pathlib import Path

import fitz


def extract_text_from_pdf(pdf_path: str, output_json_path: str):
    """
    Extract page-wise text from a PDF and save it as JSON.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages = []

    for page_index, page in enumerate(doc):
        text = page.get_text("text")

        pages.append({
            "page_number": page_index + 1,
            "text": text.strip()
        })

    output_path = Path(output_json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    print(f"Text extracted from: {pdf_path}")
    print(f"Saved to: {output_json_path}")
    print(f"Total pages: {len(pages)}")

    return pages


if __name__ == "__main__":
    extract_text_from_pdf(
        "input_docs/sample_report.pdf",
        "extracted/sample_text.json"
    )

    extract_text_from_pdf(
        "input_docs/thermal_images.pdf",
        "extracted/thermal_text.json"
    )