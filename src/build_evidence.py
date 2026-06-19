import json
import re
from pathlib import Path


def load_json(path: str):
    file_path = Path(path)

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest(manifest_path: str):
    path = Path(manifest_path)

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def images_from_pages(manifest_path: str, page_numbers: list[int], limit: int = 4):
    images = load_manifest(manifest_path)

    matched = [
        img for img in images
        if img.get("page_number") in page_numbers
    ]

    return matched[:limit]


def extract_thermal_readings(thermal_text_json_path: str):
    """
    Extract thermal metadata page-wise from thermal_text.json.
    """
    pages = load_json(thermal_text_json_path)

    if not pages:
        return []

    readings = []

    for page in pages:
        text = page.get("text", "")

        hotspot = re.search(r"Hotspot\s*:\s*([\d.]+\s*°C)", text)
        coldspot = re.search(r"Coldspot\s*:\s*([\d.]+\s*°C)", text)
        emissivity = re.search(r"Emissivity\s*:\s*([\d.]+)", text)
        reflected_temp = re.search(r"Reflected temperature\s*:\s*([\d.]+\s*°C)", text)
        thermal_image = re.search(r"Thermal image\s*:\s*([A-Za-z0-9_.-]+)", text)
        date = re.search(r"(\d{2}/\d{2}/\d{2})", text)

        # Fixed: this stops before "Serial Number"
        device = re.search(
            r"Device\s*:\s*(.+?)(?:Serial Number|$)",
            text,
            re.DOTALL
        )

        readings.append({
            "page_number": page.get("page_number"),
            "thermal_image": thermal_image.group(1) if thermal_image else "Not Available",
            "hotspot": hotspot.group(1) if hotspot else "Not Available",
            "coldspot": coldspot.group(1) if coldspot else "Not Available",
            "emissivity": emissivity.group(1) if emissivity else "Not Available",
            "reflected_temperature": reflected_temp.group(1) if reflected_temp else "Not Available",
            "device": " ".join(device.group(1).split()) if device else "Not Available",
            "date": date.group(1) if date else "Not Available",
            "area_mapping": "Not Available",
            "images": []
        })

    return readings


def build_evidence_json():
    """
    Build structured evidence JSON from the inspection and thermal reports.

    This evidence JSON keeps full image paths for DOCX generation.
    Groq receives only compact evidence from generate_report.py.
    """
    evidence = {
        "property_details": {
            "property_type": "Flat",
            "flat_no": "Flat No. 103",
            "floors": "11",
            "inspection_date_time": "27.09.2022 14:28 IST",
            "inspected_by": "Krushna & Mahesh",
            "previous_structural_audit_done": "No",
            "previous_repair_work_done": "No",
            "customer_name": "Not Available",
            "mobile": "Not Available",
            "email": "Not Available",
            "address": "Not Available",
            "property_age": "Not Available"
        },

        "observations": [
            {
                "id": 1,
                "impacted_area": "Hall",
                "negative_side_observation": "Dampness observed at skirting level of Hall of Flat No. 103",
                "probable_positive_side_source": "Gaps between tile joints of Common Bathroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate",
                "reasoning": "Skirting-level dampness indicates moisture movement. Checklist findings mention all-time leakage and possible concealed plumbing-related leakage."
            },
            {
                "id": 2,
                "impacted_area": "Common Bedroom",
                "negative_side_observation": "Dampness observed at skirting level of Common Bedroom of Flat No. 103",
                "probable_positive_side_source": "Gaps between tile joints of Common Bathroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate",
                "reasoning": "Dampness at skirting level suggests moisture movement from nearby wet areas."
            },
            {
                "id": 3,
                "impacted_area": "Master Bedroom",
                "negative_side_observation": "Dampness observed at skirting level of Master Bedroom of Flat No. 103",
                "probable_positive_side_source": "Gaps between tile joints of Master Bedroom Bathroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate",
                "reasoning": "Dampness is linked with bathroom tile joint gaps, which can allow water seepage below tile surfaces."
            },
            {
                "id": 4,
                "impacted_area": "Kitchen",
                "negative_side_observation": "Dampness observed at skirting level of Kitchen of Flat No. 103",
                "probable_positive_side_source": "Gaps between tile joints of Master Bedroom Bathroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate",
                "reasoning": "Moisture-related dampness is reported at skirting level. Exact path of moisture movement is not fully available."
            },
            {
                "id": 5,
                "impacted_area": "Master Bedroom Wall",
                "negative_side_observation": "Dampness and efflorescence observed on wall surface of Master Bedroom of Flat No. 103",
                "probable_positive_side_source": "Cracks on external wall near Master Bedroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate to High",
                "reasoning": "External wall cracks can allow water ingress. Efflorescence indicates moisture movement through wall material."
            },
            {
                "id": 6,
                "impacted_area": "Parking Area",
                "negative_side_observation": "Leakage observed at Parking ceiling below Flat No. 103",
                "probable_positive_side_source": "Plumbing issue and gaps between tile joints of Common Bathroom of Flat No. 103",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "High",
                "reasoning": "Ceiling leakage below the flat indicates active water movement and possible plumbing involvement."
            },
            {
                "id": 7,
                "impacted_area": "Common Bathroom",
                "negative_side_observation": "Mild dampness observed at ceiling of Common Bathroom of Flat No. 103",
                "probable_positive_side_source": "Gap between tile joints of Common and Master Bedroom Bathrooms of Flat No. 203",
                "inspection_source": "Sample Report summary table",
                "related_images": [],
                "severity": "Moderate",
                "reasoning": "Mild dampness is present and may be linked to tile joint gaps from upper flat bathrooms."
            }
        ],

        "checklist_findings": {
            "leakage_during": "All time",
            "leakage_due_to_concealed_plumbing": "Yes",
            "leakage_due_to_nahani_trap_or_brickbat_coba_damage": "Yes",
            "tile_joint_gaps": "Yes",
            "gaps_around_nahani_trap": "Yes",
            "loose_plumbing_joints_or_rust_around_joints": "Yes",
            "tiles_broken_or_loosed": "No",
            "external_wall_cracks": "Moderate",
            "external_plumbing_pipes_condition": "Moderate",
            "algae_fungus_moss_on_external_wall": "Moderate"
        },

        "thermal_readings": [],

        "recommended_actions": [
            "Seal gaps between tile joints in Common Bathroom and Master Bedroom Bathroom.",
            "Inspect concealed plumbing lines and repair any leakage points.",
            "Repair gaps around Nahani trap joints and plumbing outlet joints.",
            "Seal external wall cracks near the Master Bedroom area.",
            "Treat damp affected wall surfaces after the source of moisture is repaired.",
            "Monitor Parking Area ceiling leakage after bathroom/plumbing repairs.",
            "Reinspect affected areas after repair to confirm moisture reduction."
        ],

        "missing_or_unclear_information": [
            "Customer Name",
            "Mobile",
            "Email",
            "Address",
            "Property Age",
            "Exact mapping between every thermal image and impacted area"
        ]
    }

    inspection_manifest = "extracted/inspection_images_manifest.json"
    thermal_manifest = "extracted/thermal_pages_manifest.json"

    # Page mapping based on provided Sample Report layout.
    observation_page_map = {
        1: [3],
        2: [3, 4],
        3: [4],
        4: [4, 5],
        5: [5],
        6: [5, 6],
        7: [6]
    }

    for obs in evidence["observations"]:
        obs_id = obs["id"]
        pages = observation_page_map.get(obs_id, [])

        obs["related_images"] = images_from_pages(
            inspection_manifest,
            pages,
            limit=4
        )

    thermal_readings = extract_thermal_readings("extracted/thermal_text.json")

    for reading in thermal_readings:
        page_number = reading.get("page_number")

        reading["images"] = images_from_pages(
            thermal_manifest,
            [page_number],
            limit=1
        )

    evidence["thermal_readings"] = thermal_readings

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "evidence.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    print(f"Evidence JSON created: {output_path}")
    print(f"Observations: {len(evidence['observations'])}")
    print(f"Thermal readings: {len(evidence['thermal_readings'])}")

    return evidence


if __name__ == "__main__":
    build_evidence_json()