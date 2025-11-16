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

    report_mrn = pid.get("mrn", "")
    report_name = pid.get("name", "")
    report_dob = pid.get("dateOfBirth", "")

    matched_patient = patient_manager.match_patient(report_mrn, report_name, report_dob)

    if not matched_patient:
        print("ERROR: No matching patient found. Transmission NOT stored.")
        return

    matched_patient.add_transmission(report)
    if patient_manager.save_patients():
        print(f"\nSUCCESS: Report matched and stored for patient {matched_patient.Name} (MRN: {matched_patient.MRN})")
    else:
        print("ERROR: Could not save updated patient data.")
