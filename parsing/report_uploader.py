# Auth/parsing/report_uploader.py
import json
from .hl7_parser import parse_hl7_file
from .pdf_parser import parse_pdf_report
from Auth.user_management import get_current_user
from Auth.patient_management import PatientManager

def upload_report():
    current_user = get_current_user()

    if not current_user:
        print("ERROR: User not authenticated.")
        return

    if current_user.role not in ["doctor", "nurse"]:
        print("ERROR: Only doctors and nurses can upload reports.")
        return

    file_path = input("Enter file path (.hl7 or .pdf): ").strip()

    if not (file_path.endswith(".hl7") or file_path.endswith(".pdf")):
        print("ERROR: Unsupported file type.")
        return

    report = None
    errors = []

    # --- Parse HL7 ---
    if file_path.endswith(".hl7"):
        report, errors = parse_hl7_file(file_path)
        if report:
            print("\nSUCCESS: HL7 parsed successfully!")
        else:
            print("\nERROR: Corrupted HL7 file.")

    # --- Parse PDF ---
    if file_path.endswith(".pdf"):
        report, errors = parse_pdf_report(file_path)
        if report:
            print("\nSUCCESS: PDF parsed successfully!")
        else:
            print("\nERROR: Failed to parse PDF.")

    

    if not report:
        return

    # --- Patient Matching ---
    patient_manager = PatientManager()
    pid = report.get("patientIdentifiers", {})

    # First try exact match
    matched_patient = patient_manager.match_patient(
        pid.get("mrn", ""), 
        pid.get("name", ""), 
        pid.get("dateOfBirth", "")
    )

    if matched_patient:
        print(f"Exact match found: {matched_patient.Name} ({matched_patient.MRN})")
    else:
        print("No exact match found. Attempting fuzzy matching...")
        matched_patient, confidence, details = patient_manager.fuzzy_match_patient(pid)
        if matched_patient:
            print(f"Found potential match: {matched_patient.Name} ({matched_patient.MRN})")
            print(f"Match confidence: {confidence}% (MRN: {details['mrn_score']}%, Name: {details['name_score']}%, DOB: {details['dob_score']}%)")
            if confidence < 85:
                print(f"WARNING: Low confidence match ({confidence}%). Please verify patient.")
        else:
            print(f"ERROR: No match found above threshold ({confidence}%). Transmission NOT stored.")
            return
