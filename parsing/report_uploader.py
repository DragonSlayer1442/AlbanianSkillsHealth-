import json
from .hl7_parser import parse_hl7_file
from .pdf_parser import parse_pdf_report
from Auth.user_management import get_current_user


def upload_report():
    current_user = get_current_user()

    # Auth
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

    # HL7
    if file_path.endswith(".hl7"):
        report, errors = parse_hl7_file(file_path)

        if report:
            print("\nSUCCESS: HL7 parsed successfully!")
            print(json.dumps(report, indent=4))
        else:
            print("\nERROR: Corrupted HL7 file.")

        if errors:
            print("\n--- ERRORS / WARNINGS ---")
            for e in errors:
                print("•", e)
        return

    # PDF
    if file_path.endswith(".pdf"):
        report, errors = parse_pdf_report(file_path)

        if report:
            print("\nSUCCESS: PDF parsed successfully!")
            print(json.dumps(report, indent=4))
        else:
            print("\nERROR: Failed to parse PDF.")

        if errors:
            print("\n--- ERRORS / WARNINGS ---")
            for e in errors:
                print("•", e)
        return
