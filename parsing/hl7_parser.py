import os
import uuid

def parse_hl7_file(file_path):
    errors = []

    # File exists
    if not os.path.exists(file_path):
        return None, ["ERROR: File not found."]

    # Safe UTF-8
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception:
        return None, ["ERROR: Could not read HL7 file — invalid encoding."]

    if not lines:
        return None, ["ERROR: HL7 file is empty."]

    report_id = str(uuid.uuid4())
    report_date = None
    message_type = None
    patient_identifiers = {}
    observations = []

    # --- PARSING ---
    for i, line in enumerate(lines, start=1):
        if "|" not in line:
            errors.append(f"Invalid segment format at line {i}: '{line}'")
            continue

        parts = line.split('|')
        segment = parts[0]

        try:
            if segment == "MSH":
                report_date = parts[6] if len(parts) > 6 else None
                message_type = parts[8] if len(parts) > 8 else None

            elif segment == "PID":
                patient_identifiers = {
                    "mrn": parts[3] if len(parts) > 3 else None,
                    "name": parts[5] if len(parts) > 5 else None,
                    "dateOfBirth": parts[7] if len(parts) > 7 else None
                }

            elif segment == "OBX":
                code = None
                if len(parts) > 3 and parts[3]:
                    code = parts[3].split('^')[0]

                observations.append({
                    "code": code,
                    "value": parts[4] if len(parts) > 4 else None,
                    "unit": parts[5] if len(parts) > 6 else None,
                    "referenceRange": parts[6] if len(parts) > 7 else None,
                    "abnormalFlag": parts[7] if len(parts) > 8 else None,
                })

            else:
                errors.append(f"Unknown segment '{segment}' at line {i}")

        except Exception:
            errors.append(f"Corrupted HL7 segment at line {i}: '{line}'")

    if not patient_identifiers:
        errors.append("ERROR: PID segment missing.")

    if not observations:
        errors.append("ERROR: No OBX segments found.")

    if not patient_identifiers or not observations:
        return None, errors

    report = {
        "reportId": report_id,
        "reportDate": report_date,
        "messageType": message_type,
        "patientIdentifiers": patient_identifiers,
        "observations": observations
    }

    return report, errors
