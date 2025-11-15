import os
import json

USERS_PATH = os.path.join(os.path.dirname(__file__), "../DB/users.json")
SESSION_PATH = os.path.join(os.path.dirname(__file__), "../DB/session.json")
PATIENTS_PATH = os.path.join(os.path.dirname(__file__), "../DB/patients.json")

def ensure_files():
    if not os.path.exists(USERS_PATH):
        with open(USERS_PATH, "w") as f:
            json.dump({"users":[]}, f)
    if not os.path.exists(SESSION_PATH):
        with open(SESSION_PATH, "w") as f:
            json.dump([], f, indent=4)
    if not os.path.exists(PATIENTS_PATH):
        with open(PATIENTS_PATH, "w") as f:
            json.dump([], f, indent=4)        

def read_users():
    ensure_files()
    try:
        with open(USERS_PATH, 'r') as f:
            data = json.load(f)
            return data.get("users", [])
    except:
        return []

def write_users(users):
    try:
        with open(USERS_PATH, 'w') as f:
            json.dump({"users": users}, f, indent=4)
        return True
    except:
        return False

def read_logs():
    ensure_files()
    try:
        with open(SESSION_PATH, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            return logs
    except:
        return []

def write_logs(logs):
    try:
        with open(SESSION_PATH, 'w') as f:
            json.dump(logs, f, indent=4)
    except:
        print("ERROR: Could not save log")

def read_patients():
    ensure_files()
    try:
        with open(PATIENTS_PATH, "r") as f:
            patients = json.load(f)
            if not isinstance(patients, list):
                return []
            return patients
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def write_patients(patients):
    try:
        with open(PATIENTS_PATH, "w") as f:
            json.dump(patients, f, indent=4)
        return True
    except Exception as e:
        print(f"ERROR: Could not save patients. {e}")
        return False
