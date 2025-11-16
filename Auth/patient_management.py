# Auth/patient_management.py
import os
import re
import uuid
import json
from datetime import datetime
from .user_management import get_current_user
from .db_utils import read_patients, write_patients

class Patient:
    def __init__(self, MRN, Name, DOB, AssignedDoctor, patientID=None, Transmissions=None):
        self.patientID = patientID if patientID else str(uuid.uuid4())
        self.MRN = MRN
        self.Name = Name
        self.DOB = DOB
        self.AssignedDoctor = AssignedDoctor
        self.Transmissions = Transmissions if Transmissions else []

    def to_dict(self):
        return {
            "patientID": self.patientID,
            "MRN": self.MRN,
            "Name": self.Name,
            "DOB": self.DOB,
            "AssignedDoctor": self.AssignedDoctor,
            "Transmissions": self.Transmissions
        }

    def add_transmission(self, report_json: dict):
        self.Transmissions.append(report_json)


def validate_mrn(mrn):
    if not mrn:
        print("ERROR: MRN cannot be empty.")
        return False
    pattern = r"^MRN\d{7}$"
    patients = read_patients()
    for patient in patients:
        if patient["MRN"] == mrn:
            print("ERROR: MRN already exists. Please use a different MRN.")
            return False
    if not re.match(pattern, mrn):
        print("ERROR: MRN format invalid. Expected MRN followed by 7 digits (e.g., MRN1234567).")
        return False
    return True

def validate_name(name):
    if not name.strip():
        print("ERROR: Patient name cannot be empty.")
        return False
    return True

def validate_dob(dob):
    try:
        datetime.strptime(dob, "%m/%d/%Y")
        return True
    except ValueError:
        print("ERROR: Invalid date format. Expected MM/DD/YYYY.")
        return False

def create_patient():
    current_user = get_current_user()
    if not current_user:
        print("ERROR: User not authenticated. Please login first.")
        return
    if current_user.role != "doctor":
        print("ERROR: Only doctors can create patients.")
        return

    mrn = input("Enter Patient MRN (format MRN1234567): ").strip()
    if not validate_mrn(mrn):
        return

    name = input("Enter Patient Full Name: ").strip()
    if not validate_name(name):
        return

    dob = input("Enter Date of Birth (MM/DD/YYYY): ").strip()
    if not validate_dob(dob):
        return

    patient_record = Patient(mrn, name, dob, current_user.username)
    patients = read_patients()
    patients.append(patient_record.to_dict())
    if write_patients(patients):
        print(f"SUCCESS: Patient '{name}' created successfully with PatientID {patient_record.patientID}.")

#PATIENT SEARCH#

def search_patients_for_doctor(query, doctor_username):

    query = query.strip().lower()
    if not query:
        print("ERROR: Search query cannot be empty.")
        return []

    manager = PatientManager()
    results = []

    # Filter patients assigned to this doctor
    assigned_patients = [p for p in manager.patients if p.AssignedDoctor.lower() == doctor_username.lower()]

    # MRN search 
    for p in assigned_patients:
        if query in p.MRN.lower():
            results.append(p)

    # If MRN found, return immediately
    if results:
        return results

    # Name search (partial, case-insensitive)
    for p in assigned_patients:
        if query in p.Name.lower():
            results.append(p)

    return results


def display_patient_details(p):
    print("\n=== Patient Details ===")
    print(f"Name: {p.Name}")
    print(f"MRN: {p.MRN}")
    print(f"DOB: {p.DOB}")
    print(f"Assigned Doctor: {p.AssignedDoctor}")
    print(f"Total Transmissions: {len(p.Transmissions)}")


def search_patient():
    current_user = get_current_user()
    if not current_user:
        print("ERROR: User not authenticated. Please login first.")
        return
    if current_user.role != "doctor":
        print("ERROR: Permission denied. Only doctors can search patients.")
        return

    query = input("Enter search query: ").strip()
    if not query:
        print("ERROR: Search query cannot be empty.")
        return

    matches = search_patients_for_doctor(query, current_user.username)
    if not matches:
        print(f"ERROR: No patients found matching '{query}'.")
        return

    # Auto-display if only one match
    if len(matches) == 1:
        print("Found 1 patient. Displaying details...")
        display_patient_details(matches[0])
        return

    # Multiple matches - show numbered list
    print("\n=== Search Results ===")
    print(f"Found {len(matches)} patients:")
    for i, p in enumerate(matches, start=1):
        print(f"{i}. {p.Name} (MRN: {p.MRN}, DOB: {p.DOB}) - {len(p.Transmissions)} transmissions")

    while True:
        choice = input("Enter patient number to view details, or 'back' to return: ").strip()
        if choice.lower() == "back":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            display_patient_details(matches[int(choice)-1])
            return
        print("Invalid input. Try again.")


class PatientManager:
    def __init__(self):
        self.patients = [Patient(**p) for p in read_patients()]

    def save_patients(self):
        return write_patients([p.to_dict() for p in self.patients])

    # NORMALIZATION HELPERS

    def normalize_mrn(self, mrn: str) -> str:
        """Extract digits only from MRN, MRN-0022-445 -> 0022445"""
        if not mrn:
            return ""
        return "".join(re.findall(r"\d+", mrn))

    def normalize_name(self, name: str) -> str:
        """Lowercase, remove non-letter symbols, compress spaces, split by '^' if exists"""
        if not name:
            return ""
        # Replace HL7 separator '^' with space
        name = name.replace("^", " ")
        cleaned = re.sub(r"[^a-zA-Z\s]", "", name).strip().lower()
        return " ".join(cleaned.split())

    def normalize_dob(self, dob: str) -> str:
        """Normalize DOB into YYYY-MM-DD"""
        if not dob:
            return ""
        dob = dob.strip()
        # Try multiple formats
        formats = ["%Y%m%d", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(dob, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        return dob  # fallback

    # MATCHING LOGIC

    def match_patient(self, mrn: str, name: str, dob: str):
        """
        Match a patient using normalized MRN, name, and DOB.
        """
        target_mrn = self.normalize_mrn(mrn)
        target_name = self.normalize_name(name)
        target_dob = self.normalize_dob(dob)

        # -------- Primary: MRN match -------- #
        if target_mrn:
            for p in self.patients:
                p_mrn = self.normalize_mrn(p.MRN)
                if p_mrn == target_mrn:
                    print("\n")
                    print(f"Primary MRN match found: {p.Name} ({p.MRN})")
                    print("Match Confidence : 100%")
                    return p  # exact MRN match

        # -------- Secondary: Name + DOB match -------- #
        target_name_and_dob = target_name and target_dob
        if target_name_and_dob:
            for p in self.patients:
                p_name = self.normalize_name(p.Name)
                p_dob = self.normalize_dob(p.DOB)
                if p_name == target_name and p_dob == target_dob:
                    print(f"Secondary Name+DOB match found: {p.Name} ({p.MRN})")
                    print("Match Confidence : 80%")
                    return p  # exact name + DOB match

        return None

