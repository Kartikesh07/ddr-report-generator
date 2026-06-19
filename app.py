from pathlib import Path
import shutil

import streamlit as st

from src.extract_text import extract_text_from_pdf
from src.extract_images import extract_inspection_images, render_thermal_pages
from src.build_evidence import build_evidence_json
from src.generate_report import generate_ddr
from src.validate_report import validate_report
from src.create_docx import create_docx


def reset_runtime_folders():
    """
    Clear old extracted/output data so old logo/header images don't remain.
    """
    for folder in ["extracted", "output"]:
        path = Path(folder)

        if path.exists():
            shutil.rmtree(path)

        path.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file, path: str):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(uploaded_file.read())


st.set_page_config(
    page_title="AI DDR Report Generator",
    layout="wide"
)

st.title("AI DDR Report Generator")
st.write(
    "Upload Inspection Report and Thermal Report to generate a structured "
    "Detailed Diagnostic Report with text, inspection images, thermal evidence, and validation."
)

inspection_pdf = st.file_uploader(
    "Upload Inspection Report PDF",
    type=["pdf"]
)

thermal_pdf = st.file_uploader(
    "Upload Thermal Report PDF",
    type=["pdf"]
)

if st.button("Generate DDR"):
    if not inspection_pdf or not thermal_pdf:
        st.error("Please upload both Inspection Report and Thermal Report.")
    else:
        try:
            reset_runtime_folders()

            input_dir = Path("input_docs")
            input_dir.mkdir(parents=True, exist_ok=True)

            inspection_path = "input_docs/sample_report.pdf"
            thermal_path = "input_docs/thermal_images.pdf"

            save_uploaded_file(inspection_pdf, inspection_path)
            save_uploaded_file(thermal_pdf, thermal_path)

            st.info("Step 1: Extracting text from PDFs...")
            extract_text_from_pdf(
                inspection_path,
                "extracted/sample_text.json"
            )
            extract_text_from_pdf(
                thermal_path,
                "extracted/thermal_text.json"
            )

            st.info("Step 2: Extracting inspection images...")
            extract_inspection_images(
                inspection_path,
                "extracted/inspection_images"
            )

            st.info("Step 3: Rendering thermal pages...")
            render_thermal_pages(
                thermal_path,
                "extracted/thermal_pages"
            )

            st.info("Step 4: Building evidence JSON...")
            evidence = build_evidence_json()

            st.info("Step 5: Generating DDR using Groq...")
            report = generate_ddr()

            st.info("Step 6: Validating DDR...")
            validation = validate_report()

            st.info("Step 7: Creating DOCX...")
            create_docx()

            st.success("DDR generated successfully!")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Generated DDR Preview")
                st.markdown(report)

            with col2:
                st.subheader("Validation Result")
                st.code(validation)

                st.subheader("Extraction Summary")
                st.write(f"Observations: {len(evidence.get('observations', []))}")
                st.write(f"Thermal readings: {len(evidence.get('thermal_readings', []))}")

            docx_path = Path("output/generated_ddr.docx")
            evidence_path = Path("output/evidence.json")
            validation_path = Path("output/validation_report.json")

            if docx_path.exists():
                with open(docx_path, "rb") as f:
                    st.download_button(
                        label="Download Generated DDR DOCX",
                        data=f,
                        file_name="generated_ddr.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

            if evidence_path.exists():
                with open(evidence_path, "rb") as f:
                    st.download_button(
                        label="Download Evidence JSON",
                        data=f,
                        file_name="evidence.json",
                        mime="application/json"
                    )

            if validation_path.exists():
                with open(validation_path, "rb") as f:
                    st.download_button(
                        label="Download Validation Report",
                        data=f,
                        file_name="validation_report.json",
                        mime="application/json"
                    )

        except Exception as e:
            st.error(f"Something went wrong: {e}")