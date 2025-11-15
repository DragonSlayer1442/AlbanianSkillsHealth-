# Auth/patient_management.py
import os
import uuid
import json
from datetime import datetime
from .user_management import get_current_user
from .db_utils import read_patients, write_patients

class Patient:
    def __init__(self, mrn, name, dob, assigned_doctor):
        self.patientID = str(uuid.uuid4())
        self.MRN = mrn
        self.Name = name
        self.DOB = dob
        self.AssignedDoctor = assigned_doctor
        self.Transmissions = []

    def to_dict(self):
        return {
            "patientID": self.patientID,
            "MRN": self.MRN,
            "Name": self.Name,
            "DOB": self.DOB,
            "AssignedDoctor": self.AssignedDoctor,
            "Transmissions": self.Transmissions
        }

def validate_mrn(mrn):
    import re
    if not mrn:
        print("ERROR: MRN cannot be empty.")
        return False
    pattern = r"^MRN\d{6}$"
    patients = read_patients()
    for patient in patients:
        if patient["MRN"] == mrn:
            print("ERROR: MRN already exists. Please use a different MRN.")
            return False
    if not re.match(pattern, mrn):
        print("ERROR: MRN format invalid. Expected MRN followed by 6 digits (e.g., MRN123456).")
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

    mrn = input("Enter Patient MRN (format MRN123456): ").strip()
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
