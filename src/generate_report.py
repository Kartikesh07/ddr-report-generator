import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


SYSTEM_PROMPT = """
You are an expert building inspection report writer.

Generate a Detailed Diagnostic Report using ONLY the provided compact evidence.

Strict rules:
- Do not invent facts.
- If information is missing, write "Not Available".
- If thermal image to area mapping is unclear, mention it clearly.
- Avoid duplicate observations.
- Use simple client-friendly language.
- Keep root cause statements probable, not absolute.
- Do not write image filenames.
- Do not mention internal JSON.
"""


USER_PROMPT_TEMPLATE = """
Generate a client-ready Detailed Diagnostic Report with these exact sections:

1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment with Reasoning
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

Important:
- Use bullet points, not numbered lists, inside sections.
- Mention that visual images are included in the visual evidence section.
- Mention that thermal images are included as reference evidence.
- If exact room-wise mapping of thermal images is not available, write "Not Available".
- Do not say thermal images are unavailable if thermal_summary says thermal pages exist.
- Do not write image filenames inside the main report.
- Keep the report concise and client-friendly.

Compact Evidence:
{compact_evidence}
"""


def compact_evidence_for_llm(evidence: dict) -> dict:
    """
    Removes heavy fields like image paths, width, height, filenames, etc.
    Keeps only facts needed for report writing.
    """

    compact_observations = []

    for obs in evidence.get("observations", []):
        compact_observations.append({
            "id": obs.get("id", "Not Available"),
            "impacted_area": obs.get("impacted_area", "Not Available"),
            "negative_side_observation": obs.get("negative_side_observation", "Not Available"),
            "probable_positive_side_source": obs.get("probable_positive_side_source", "Not Available"),
            "severity": obs.get("severity", "Not Available"),
            "reasoning": obs.get("reasoning", "Not Available")
        })

    thermal_readings = evidence.get("thermal_readings", [])

    hotspots = []
    coldspots = []

    for reading in thermal_readings:
        hotspot = reading.get("hotspot", "")
        coldspot = reading.get("coldspot", "")

        try:
            if hotspot and hotspot != "Not Available":
                hotspots.append(float(hotspot.replace("°C", "").strip()))
        except Exception:
            pass

        try:
            if coldspot and coldspot != "Not Available":
                coldspots.append(float(coldspot.replace("°C", "").strip()))
        except Exception:
            pass

    thermal_summary = {
        "thermal_pages_available": len(thermal_readings),
        "thermal_images_available": "Yes" if len(thermal_readings) > 0 else "No",
        "exact_area_mapping": "Not Available",
        "hotspot_range": (
            f"{min(hotspots)} °C to {max(hotspots)} °C"
            if hotspots else "Not Available"
        ),
        "coldspot_range": (
            f"{min(coldspots)} °C to {max(coldspots)} °C"
            if coldspots else "Not Available"
        ),
        "sample_thermal_readings": [
            {
                "page_number": r.get("page_number", "Not Available"),
                "hotspot": r.get("hotspot", "Not Available"),
                "coldspot": r.get("coldspot", "Not Available"),
                "emissivity": r.get("emissivity", "Not Available"),
                "reflected_temperature": r.get("reflected_temperature", "Not Available"),
                "device": r.get("device", "Not Available")
            }
            for r in thermal_readings[:5]
        ]
    }

    compact = {
        "property_details": evidence.get("property_details", {}),
        "observations": compact_observations,
        "checklist_findings": evidence.get("checklist_findings", {}),
        "thermal_summary": thermal_summary,
        "recommended_actions": evidence.get("recommended_actions", []),
        "missing_or_unclear_information": evidence.get("missing_or_unclear_information", [])
    }

    return compact


def call_groq_with_retry(messages, temperature=0.1, max_completion_tokens=2500, retries=5):
    """
    Handles temporary Groq rate limit by waiting and retrying.
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            error_text = str(e)

            if "429" in error_text or "rate_limit" in error_text:
                wait_time = 15 + attempt * 10
                print(f"Rate limit hit. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            if "413" in error_text or "Request too large" in error_text:
                raise Exception(
                    "Groq request is still too large. Reduce compact evidence more or lower max_completion_tokens."
                )

            raise e

    raise Exception("Groq rate limit still active after retries.")


def generate_ddr():
    evidence_path = Path("output/evidence.json")

    if not evidence_path.exists():
        raise FileNotFoundError("output/evidence.json not found. Run build_evidence.py first.")

    with open(evidence_path, "r", encoding="utf-8") as f:
        evidence = json.load(f)

    compact_evidence = compact_evidence_for_llm(evidence)

    compact_path = Path("output/compact_evidence_for_llm.json")
    compact_path.parent.mkdir(parents=True, exist_ok=True)

    with open(compact_path, "w", encoding="utf-8") as f:
        json.dump(compact_evidence, f, indent=2, ensure_ascii=False)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        compact_evidence=json.dumps(compact_evidence, indent=2, ensure_ascii=False)
    )

    report = call_groq_with_retry(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1,
        max_completion_tokens=2500
    )

    output_path = Path("output/generated_ddr.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Compact evidence saved: {compact_path}")
    print(f"DDR markdown generated: {output_path}")

    return report


if __name__ == "__main__":
    print(generate_ddr())