import os
import uuid
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


def parse_pdf_report(file_path):
    if PyPDF2 is None:
        return None, ["ERROR: PyPDF2 not installed. Install it with: pip install PyPDF2"]

    if not os.path.exists(file_path):
        return None, ["ERROR: File not found."]

    try:
        reader = PyPDF2.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception:
        return None, ["ERROR: Failed to extract text from PDF file."]

    if not text.strip():
        return None, ["ERROR: PDF text extraction returned empty content."]

    errors = []
    report_id = str(uuid.uuid4())

    # Helper for regex fields
    def find(pattern, label):
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            errors.append(f"ERROR: Could not find '{label}' in PDF.")
            return None
        return match.group(1).strip()

    # Extract patient data
    patient_name = find(r"Patient Name:\s*(.*)", "Patient Name")
    mrn = find(r"MRN:\s*(.*)", "MRN")
    dob = find(r"Date of Birth:\s*(.*)", "Date of Birth")
    report_date = find(r"Report Date:\s*(.*)", "Report Date")

    # Extract clinical observations
    heart_rate = find(r"Heart Rate:\s*(\d+)", "Heart Rate")
    rhythm = find(r"Rhythm:\s*(.*)", "Rhythm")

    observations = []
    if heart_rate:
        observations.append({
            "code": "HR",
            "value": heart_rate,
            "unit": "bpm",
            "referenceRange": "60-100",
            "abnormalFlag": None
        })

    if rhythm:
        observations.append({
            "code": "RHY",
            "value": rhythm,
            "unit": None,
            "referenceRange": None,
            "abnormalFlag": None
        })

    if not patient_name or not mrn:
        return None, errors

    report = {
        "reportId": report_id,
        "reportDate": report_date,
        "messageType": "PDF_REPORT",
        "patientIdentifiers": {
            "mrn": mrn,
            "name": patient_name,
            "dateOfBirth": dob
        },
        "observations": observations
    }

    return report, errors
