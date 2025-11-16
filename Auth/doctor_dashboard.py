# Auth/doctor_dashboard.py
from datetime import datetime
from .user_management import get_current_user
from .db_utils import read_patients


def parse_report_date(report_date_str: str) -> str:
    """
    Convert HL7-style timestamp like 20240116120000 -> '2024-01-16 12:00:00'
    """
    if not report_date_str:
        return ""
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d%H%M", "%Y%m%d"):
        try:
            dt = datetime.strptime(report_date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
    return report_date_str


def format_observation(obs: dict) -> str:
    code = obs.get("code") or obs.get("observation", "Unknown")
    value = obs.get("value") or ""
    unit_raw = obs.get("unit") or ""
    # "bpm^beats per minute^UCUM" - bpm per minute
    unit = ""
    if unit_raw:
        unit_parts = unit_raw.split("^")
        if len(unit_parts) >= 2 and unit_parts[1].strip():
            unit = unit_parts[1].strip()
        else:
            unit = unit_parts[0].strip()
    ref = obs.get("referenceRange") or ""
    abn = obs.get("abnormalFlag") or ""
    parts = [f"{code}:"]
    if value:
        parts.append(f"{value}")
    if unit:
        parts.append(f"{unit}")
    if ref:
        parts.append(f"(Reference: {ref})")
    if abn:
        parts.append(f"({abn})")
    return " ".join(parts)


def list_my_patients(doctor_username: str):
    patients = read_patients()
    my = [p for p in patients if p.get("AssignedDoctor") == doctor_username]
    if not my:
        print("\n=== My Patients ===")
        print("No patients assigned to you.")
        return None
    print("\n=== My Patients ===")
    for i, p in enumerate(my, start=1):
        name = p.get("Name", "Unknown")
        mrn = p.get("MRN", "Unknown")
        dob = p.get("DOB", "Unknown")
        transmissions = p.get("Transmissions", []) or []
        print(f"{i}. {name} (MRN: {mrn}, DOB: {dob}) - {len(transmissions)} transmissions")
    print(f"{len(my)+1}. Back to dashboard")
    # choose
    while True:
        choice = input("Enter patient number to view details: ").strip()
        if choice.lower() in ("back", str(len(my)+1)):
            return None
        if not choice.isdigit():
            print("Invalid input. Enter a number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(my):
            show_patient_details(my[idx - 1])
            return None
        else:
            print("Number out of range.")


def list_recent_transmissions(doctor_username: str):
    patients = read_patients()
    transmissions = []
    for p in patients:
        if p.get("AssignedDoctor") != doctor_username:
            continue
        for t in p.get("Transmissions", []) or []:
            # unify fields for display
            transmissions.append({
                "patient": p.get("Name"),
                "patient_mrn": p.get("MRN"),
                "reportId": t.get("reportId") or t.get("transmissionID") or t.get("report_id"),
                "reportDate": t.get("reportDate") or t.get("report_date") or "",
                "raw": t
            })
    if not transmissions:
        print("\n=== Recent Transmissions ===")
        print("No transmissions found for your patients.")
        return
    # sort by reportDate if possible (descending)
    def sort_key(x):
        s = x.get("reportDate") or ""
        try:
            return datetime.strptime(s, "%Y%m%d%H%M%S")
        except Exception:
            try:
                return datetime.strptime(s, "%Y%m%d")
            except Exception:
                return datetime.min
    transmissions.sort(key=sort_key, reverse=True)
    print("\n=== Recent Transmissions ===")
    for i, t in enumerate(transmissions, start=1):
        rd = parse_report_date(t.get("reportDate") or "")
        print(f"{i}. Report ID: {t.get('reportId')} ({rd}) - Patient: {t.get('patient')} (MRN: {t.get('patient_mrn')})")
    print(f"{len(transmissions)+1}. Back to dashboard")
    while True:
        choice = input("Enter transmission number to view details, or 'back' to return: ").strip()
        if choice.lower() in ("back", str(len(transmissions)+1)):
            return
        if not choice.isdigit():
            print("Invalid input. Enter a number.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(transmissions):
            show_transmission_details(transmissions[idx - 1])
            return
        else:
            print("Number out of range.")


def show_patient_details(patient: dict):
    print(f"\n=== Patient Details: {patient.get('Name')} ===")
    print(f"MRN: {patient.get('MRN')}")
    print(f"Date of Birth: {patient.get('DOB')}")
    print(f"Assigned Doctor: {patient.get('AssignedDoctor')}")
    transmissions = patient.get("Transmissions", []) or []
    print(f"Total Transmissions: {len(transmissions)}")
    if not transmissions:
        input("Press Enter to return.")
        return
    for i, t in enumerate(transmissions, start=1):
        rd = parse_report_date(t.get("reportDate") or t.get("report_date") or "")
        print(f"{i}. Report ID: {t.get('reportId')} ({rd})")
    while True:
        choice = input("Enter transmission number to view details, or 'back' to return: ").strip()
        if choice.lower() == "back":
            return
        if not choice.isdigit():
            print("Invalid input. Enter a number or 'back'.")
            continue
        idx = int(choice)
        if 1 <= idx <= len(transmissions):
            show_transmission_details({
                "patient": patient.get("Name"),
                "patient_mrn": patient.get("MRN"),
                "reportId": transmissions[idx - 1].get("reportId"),
                "reportDate": transmissions[idx - 1].get("reportDate"),
                "raw": transmissions[idx - 1]
            })
            # after viewing go back to patient details
            print(f"\n=== Back to {patient.get('Name')} details ===")
            continue
        else:
            print("Number out of range.")


def show_transmission_details(item: dict):
    raw = item.get("raw", {})
    print("\n=== Transmission Details ===")
    print(f"Report ID: {item.get('reportId')}")
    rd = parse_report_date(item.get("reportDate") or raw.get("reportDate") or raw.get("report_date") or "")
    print(f"Report Date: {rd}")
    print(f"Patient: {item.get('patient')} (MRN: {item.get('patient_mrn')})")
    obs = raw.get("observations", []) or raw.get("obs", []) or []
    if not obs:
        print("Observations: None")
    else:
        print("Observations:")
        for i, o in enumerate(obs, start=1):
            print(f"{i}. {format_observation(o)}")
    input("Press 'back' (Enter) to return.")
    return


def run_dashboard():
    current_user = get_current_user()
    if not current_user:
        print("ERROR: User not authenticated. Please login first.")
        return
    if current_user.role != "doctor":
        print("ERROR: Permission denied. Doctor access required.")
        return

    while True:
        print("\n=== Doctor Dashboard ===")
        print("Choose view:")
        print("1. List my patients")
        print("2. List recent transmissions")
        print("3. Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            list_my_patients(current_user.username)
        elif choice == "2":
            list_recent_transmissions(current_user.username)
        elif choice == "3" or choice.lower() in ("exit", "back"):
            return
        else:
            print("Invalid option. Choose 1, 2 or 3.")
