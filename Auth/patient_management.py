import os
import json
import uuid
import re
from datetime import datetime
from .db_utils import read_patients, write_patients
from .user_management import get_current_user



def validate_mrn(mrn):
    if not mrn:
        print("ERROR: MRN cannot be empty.")
        return False
    pattern = r"^MRN\d{6}$"
    if not re.fullmatch(pattern, mrn):
        print("ERROR: MRN format invalid. Expected MRN followed by 6 digits (e.g., MRN123456).")
        return False
    patients = read_patients()
    for patient in patients:
        if isinstance(patient, dict) and patient.get("MRN") == mrn:
            print("ERROR: MRN already exists. Please use a different MRN.")
            return False
    return True

def validate_dob(dob):
    try:
        datetime.strptime(dob, "%m/%d/%Y")
        return True
    except ValueError:
        print("ERROR: Invalid date format. Expected MM/DD/YYYY.")
        return False

def validate_name(name):
    if not name.strip():
        print("ERROR: Patient name cannot be empty.")
        return False
    return True

def create_patient():
    current_user = get_current_user()
    if not current_user:
        print("ERROR: User not authenticated. Please login first.")
        return
    if current_user.get("role") != "doctor":
        print("ERROR: Only doctors can create patients.")
        return

    mrn = input("Enter Patient MRN (format MRN123456): ").strip()
    if not validate_mrn(mrn):
        return

    name = input("Enter Patient Full Name: ").strip()
    if not validate_name(name):
        return

    dob = input("Enter Date of Birth (MM/DD/YYYY): ").strip()
    if not validate_dob(dob):
        return

    patient_id = str(uuid.uuid4())
    assigned_doctor = current_user["username"]

    patient_record = {
        "patientID": patient_id,
        "MRN": mrn,
        "Name": name,
        "DOB": dob,
        "AssignedDoctor": assigned_doctor,
        "Transmissions": []
    }

    patients = read_patients()
    patients.append(patient_record)

    if write_patients(patients):
        print(f"SUCCESS: Patient '{name}' created successfully with PatientID {patient_id}.")
