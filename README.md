# AI DDR Report Generator

An AI-assisted Detailed Diagnostic Report (DDR) generator that converts an Inspection Report PDF and Thermal Report PDF into a structured, client-ready diagnostic report.

The system extracts text, visual evidence, thermal references, builds structured evidence JSON, generates a DDR using Groq, validates the output, and exports a professionally formatted DOCX report.

---

## Project Objective

This project was built for the Applied AI Builder assignment.

The goal is to generate a Detailed Diagnostic Report from two input documents:

1. Inspection Report
2. Thermal Images / Thermal Report

The generated DDR includes:

* Property Issue Summary
* Area-wise Observations
* Probable Root Cause
* Severity Assessment with Reasoning
* Recommended Actions
* Additional Notes
* Missing or Unclear Information
* Area-wise Visual Evidence
* Thermal Evidence Summary
* Selected Thermal References

---

## Key Features

* Upload Inspection Report PDF and Thermal Report PDF
* Extract text page-wise from both PDFs
* Extract inspection images from the inspection report
* Filter out logos, headers, footers, and layout artifacts
* Render thermal report pages as image references
* Extract thermal metadata such as hotspot, coldspot, emissivity, reflected temperature, and device
* Generate compact evidence JSON to reduce LLM token usage
* Generate DDR using Groq
* Validate generated output locally
* Export a professionally formatted DOCX report
* Mark missing information as `Not Available`
* Avoid unsupported or invented claims by using structured evidence

---

## Tech Stack

* Python
* Streamlit
* PyMuPDF
* python-docx
* Groq API
* python-dotenv

---

## Project Structure

```text
ddr-report-generator/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── extract_text.py
│   ├── extract_images.py
│   ├── build_evidence.py
│   ├── generate_report.py
│   ├── validate_report.py
│   └── create_docx.py
│
├── input_docs/
│   ├── sample_report.pdf
│   └── thermal_images.pdf
│
├── extracted/
│   ├── sample_text.json
│   ├── thermal_text.json
│   ├── inspection_images/
│   ├── thermal_pages/
│   ├── inspection_images_manifest.json
│   └── thermal_pages_manifest.json
│
└── output/
    ├── evidence.json
    ├── compact_evidence_for_llm.json
    ├── generated_ddr.md
    ├── validation_report.json
    └── generated_ddr.docx
```

Note: `input_docs/`, `extracted/`, and `output/` are generated or runtime folders and should not be committed to GitHub.

---

## How the System Works

```text
PDF Upload
   ↓
Text Extraction
   ↓
Image Extraction / Thermal Page Rendering
   ↓
Structured Evidence JSON
   ↓
Compact Evidence for LLM
   ↓
Groq DDR Generation
   ↓
Local Validation
   ↓
Formatted DOCX Report
```

---

## Accuracy Strategy

The system does not directly send full PDFs to the LLM.

Instead, it follows a structured pipeline:

1. Extracts text and images from the source PDFs.
2. Builds an `evidence.json` file containing only grounded inspection findings.
3. Creates a compact evidence version for Groq to reduce token usage.
4. Uses the LLM only for client-friendly report writing.
5. Keeps image insertion deterministic using `python-docx`.
6. Runs local validation for required sections, missing information, duplicate points, and thermal evidence issues.

This improves reliability and reduces hallucination risk.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ddr-report-generator.git
cd ddr-report-generator
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Recommended model for testing:

```env
GROQ_MODEL=llama-3.1-8b-instant
```

This model keeps token usage lower and helps avoid rate limit issues.

---

## Running the App

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

Upload:

1. Inspection Report PDF
2. Thermal Report PDF

Then click:

```text
Generate DDR
```

The app will generate:

* DDR preview
* Validation summary
* Downloadable DOCX report
* Evidence JSON
* Validation report JSON

---

## Running Scripts Manually

You can also run the pipeline step-by-step:

```bash
python src/extract_text.py
python src/extract_images.py
python src/build_evidence.py
python src/generate_report.py
python src/validate_report.py
python src/create_docx.py
```

Final output will be created at:

```text
output/generated_ddr.docx
```

---

## Deployment

This project can be deployed on Streamlit Community Cloud.

### Steps

1. Push the project to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select the GitHub repository.
5. Set main file path as:

```text
app.py
```

6. Add secrets in Streamlit Cloud:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "llama-3.1-8b-instant"
```

7. Deploy.

Do not commit `.env` to GitHub.

---

## `.gitignore`

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc

input_docs/
extracted/
output/

.streamlit/secrets.toml
```

---

## Output Report Format

The generated DOCX includes:

1. Cover Page
2. Property Issue Summary
3. Property Details Table
4. Area-wise Observation Table
5. Probable Root Cause
6. Severity Assessment Table
7. Recommended Actions Table
8. Additional Notes
9. Missing or Unclear Information Table
10. Area-wise Visual Evidence
11. Thermal Evidence Summary
12. Selected Thermal References

---

## Current Limitations

* Exact room-wise mapping of every thermal image is marked as `Not Available` when the thermal report does not provide explicit area labels.
* Inspection images are currently mapped using source page context. Some images may be repeated if multiple observations appear on the same page.
* The system works best with reports that follow a similar structure to the provided sample documents.
* Local validation checks structure and consistency, but it cannot fully prove every generated claim is supported. The compact evidence approach helps reduce unsupported claims.

---

## Future Improvements

* Add photo-label-level mapping for more accurate image placement.
* Use a vision model to classify images by area and defect type.
* Add human review/edit screen before final DOCX generation.
* Add PDF export in addition to DOCX.
* Add support for multiple report templates.
* Add confidence scores for every extracted observation.
* Add automatic conflict detection between inspection and thermal evidence.

---

## Author

Kartikesh Belamkar
