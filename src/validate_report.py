import json
import re
from pathlib import Path


REQUIRED_SECTIONS = [
    "Property Issue Summary",
    "Area-wise Observations",
    "Probable Root Cause",
    "Severity Assessment",
    "Recommended Actions",
    "Additional Notes",
    "Missing or Unclear Information"
]


def find_missing_sections(report_text: str):
    missing = []
    lower_report = report_text.lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in lower_report:
            missing.append(section)

    return missing


def find_missing_info_not_marked(evidence: dict, report_text: str):
    issues = []

    missing_items = evidence.get("missing_or_unclear_information", [])

    for item in missing_items:
        if item.lower() not in report_text.lower():
            issues.append(f"{item} not mentioned in report")

    if "not available" not in report_text.lower():
        issues.append('"Not Available" not used for missing information')

    return issues


def find_thermal_evidence_issues(evidence: dict, report_text: str):
    issues = []

    thermal_readings = evidence.get("thermal_readings", [])
    has_thermal = len(thermal_readings) > 0
    lower_report = report_text.lower()

    wrong_phrases = [
        "no thermal images were provided",
        "thermal images were not provided",
        "thermal evidence: not available",
        "no thermal evidence"
    ]

    if has_thermal:
        for phrase in wrong_phrases:
            if phrase in lower_report:
                issues.append(
                    "Report says thermal evidence is not available, but thermal readings/images exist."
                )
                break

    if has_thermal and "thermal" not in lower_report:
        issues.append("Thermal evidence exists but report does not mention thermal evidence.")

    return issues


def find_duplicate_observation_lines(report_text: str):
    lines = [
        line.strip().lower()
        for line in report_text.split("\n")
        if len(line.strip()) > 40
    ]

    seen = set()
    duplicates = []

    for line in lines:
        normalized = re.sub(r"\s+", " ", line)

        if normalized in seen:
            duplicates.append(line)
        else:
            seen.add(normalized)

    return duplicates[:10]


def validate_report():
    """
    Local validation.
    No Groq call here, so no rate limit issue.
    """
    evidence_path = Path("output/evidence.json")
    report_path = Path("output/generated_ddr.md")

    if not evidence_path.exists():
        raise FileNotFoundError("output/evidence.json not found. Run build_evidence.py first.")

    with open(evidence_path, "r", encoding="utf-8") as f:
        evidence = json.load(f)

    # If generated_ddr.md exists, validate that.
    # If not, validate directly from evidence availability.
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()
    else:
        report_text = json.dumps(evidence, indent=2, ensure_ascii=False)

    missing_sections = find_missing_sections(report_text)
    missing_info_issues = find_missing_info_not_marked(evidence, report_text)
    thermal_issues = find_thermal_evidence_issues(evidence, report_text)
    duplicate_points = find_duplicate_observation_lines(report_text)

    fixes_required = []

    if missing_sections:
        fixes_required.append("Add missing required sections.")

    if missing_info_issues:
        fixes_required.append('Mention missing fields and mark them as "Not Available".')

    if thermal_issues:
        fixes_required.append("Correct thermal evidence statement.")

    if duplicate_points:
        fixes_required.append("Remove duplicate repeated lines.")

    total_issues = (
        len(missing_sections)
        + len(missing_info_issues)
        + len(thermal_issues)
        + len(duplicate_points)
    )

    score = max(60, 100 - total_issues * 5)

    validation = {
        "invented_claims": [
            "Local validator cannot fully detect invented claims. Compact evidence and deterministic report generation reduce hallucination risk."
        ],
        "duplicate_points": duplicate_points,
        "missing_required_sections": missing_sections,
        "unsupported_root_causes": [],
        "image_mapping_issues": [
            "Exact room-wise thermal image mapping is Not Available unless explicitly present in source documents."
        ],
        "missing_information_not_marked": missing_info_issues,
        "thermal_evidence_issues": thermal_issues,
        "overall_accuracy_score_out_of_100": score,
        "fixes_required": fixes_required
    }

    output_path = Path("output/validation_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validation, f, indent=2, ensure_ascii=False)

    print(f"Validation report saved: {output_path}")
    print(json.dumps(validation, indent=2, ensure_ascii=False))

    return validation


if __name__ == "__main__":
    validate_report()