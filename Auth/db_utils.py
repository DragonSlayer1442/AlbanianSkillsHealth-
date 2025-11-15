# Auth/db_utils.py
import os
import json

BASE_DIR = os.path.join(os.path.dirname(__file__), "../DB")

USERS_FILE = os.path.join(BASE_DIR, "users.json")
LOGS_FILE = os.path.join(BASE_DIR, "session.json")
PATIENTS_FILE = os.path.join(BASE_DIR, "patients.json")


def ensure_file(path):
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f, indent=4)


# Users
def read_users():
    ensure_file(USERS_FILE)
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def write_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return True
    except:
        return False


# Logs (session)
def read_logs():
    ensure_file(LOGS_FILE)
    try:
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def write_logs(logs):
    try:
        with open(LOGS_FILE, "w") as f:
            json.dump(logs, f, indent=4)
        return True
    except:
        return False


# Patients
def read_patients():
    ensure_file(PATIENTS_FILE)
    try:
        with open(PATIENTS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    except:
        return []


def write_patients(patients):
    try:
        with open(PATIENTS_FILE, "w") as f:
            json.dump(patients, f, indent=4)
        return True
    except:
        return False
