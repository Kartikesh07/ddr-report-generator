import json
from pathlib import Path

import fitz


def save_manifest(records, manifest_path):
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def is_layout_asset(width: int, height: int) -> bool:
    """
    Filters layout assets like:
    - UrbanRoof logo strip
    - Header/footer lines
    - Icons
    - Very tiny images
    - Very wide decorative bars
    """
    if width <= 0 or height <= 0:
        return True

    if width < 120 or height < 120:
        return True

    aspect_ratio = width / height

    # Very wide image usually means footer/header/logo strip
    if aspect_ratio > 4.0:
        return True

    # Very thin/tall image usually means line/artifact
    if aspect_ratio < 0.20:
        return True

    return False


def extract_inspection_images(pdf_path: str, output_folder: str):
    """
    Extract actual embedded inspection/site photos from Sample Report PDF.
    Skips logos, header strips, footer lines, and icons.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir.parent / "inspection_images_manifest.json"
    image_records = []

    for page_index, page in enumerate(doc):
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = int(base_image.get("width", 0))
            height = int(base_image.get("height", 0))

            if is_layout_asset(width, height):
                continue

            image_name = f"page_{page_index + 1}_img_{img_index + 1}.{image_ext}"
            image_path = output_dir / image_name

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_records.append({
                "type": "inspection_photo",
                "page_number": page_index + 1,
                "image_name": image_name,
                "image_path": str(image_path),
                "width": width,
                "height": height
            })

    save_manifest(image_records, manifest_path)

    print(f"Inspection images extracted: {len(image_records)}")
    print(f"Inspection manifest saved: {manifest_path}")

    return image_records


def render_thermal_pages(pdf_path: str, output_folder: str):
    """
    Render each page of Thermal Images PDF as one full image.

    This is better than extracting embedded thermal images because each page contains:
    - Thermal image
    - Normal visual image
    - Hotspot/coldspot details
    - Date/device metadata
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir.parent / "thermal_pages_manifest.json"
    image_records = []

    zoom = 2.0
    matrix = fitz.Matrix(zoom, zoom)

    for page_index, page in enumerate(doc):
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        image_name = f"thermal_page_{page_index + 1}.png"
        image_path = output_dir / image_name

        pix.save(str(image_path))

        image_records.append({
            "type": "thermal_page",
            "page_number": page_index + 1,
            "image_name": image_name,
            "image_path": str(image_path),
            "width": pix.width,
            "height": pix.height
        })

    save_manifest(image_records, manifest_path)

    print(f"Thermal pages rendered: {len(image_records)}")
    print(f"Thermal manifest saved: {manifest_path}")

    return image_records


if __name__ == "__main__":
    extract_inspection_images(
        "input_docs/sample_report.pdf",
        "extracted/inspection_images"
    )

    render_thermal_pages(
        "input_docs/thermal_images.pdf",
        "extracted/thermal_pages"
    )