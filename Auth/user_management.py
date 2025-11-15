from datetime import datetime
from .db_utils import read_users, write_users, read_logs, write_logs
from .security import hash_password, check_password

_current_user = None

def login():
    global _current_user
    username = input("Enter username: ")
    password = input("Enter password: ")
    users = read_users()
    for user in users:
        if user.get("username") == username:
            if check_password(password, user.get("passwordHash", "")):
                _current_user = {"username": username, "role": user.get("role", "user")}
                print(f"SUCCESS: Logged in as {username} ({_current_user['role']})")
                logs = read_logs()
                logs.append({"username": username, "role": _current_user['role'], "loggedinAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                write_logs(logs)
                return
            else:
                print("ERROR: Invalid credentials")
                return
    print("ERROR: Invalid credentials")

def create_user():
    global _current_user
    if not _current_user or _current_user.get("role") != "admin":
        print("ERROR: Permission denied. Admin access required.")
        return
    username = input("Enter new username: ")
    password = input("Enter password: ")
    role = input("Select role (doctor/nurse): ").lower()
    if role not in ["doctor", "nurse"]:
        print("ERROR: Role must be 'doctor' or 'nurse'.")
        return
    if len(username) < 4 or len(username) > 50:
        print("ERROR: Username must be between 4 and 50 characters.")
        return
    if len(password) < 8:
        print("ERROR: Password must be at least 8 characters long.")
        return
    users = read_users()
    for user in users:
        if user["username"] == username:
            print("ERROR: Username already exists")
            return
    hashed = hash_password(password)
    users.append({"username": username, "passwordHash": hashed, "role": role})
    if write_users(users):
        print(f"SUCCESS: User '{username}' created successfully.")

def logout():
    global _current_user
    if _current_user is None:
        print("INFO: No user is currently logged in.")
        return
    print(f"SUCCESS: User '{_current_user['username']}' has been logged out.")
    _current_user = None


def get_current_user():
    return _current_user
