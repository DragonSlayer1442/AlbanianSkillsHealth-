# Auth/user_management.py
from datetime import datetime
from .db_utils import read_users, write_users, read_logs, write_logs
from .security import hash_password, check_password

_current_user = None

class User:
    def __init__(self, username, password_hash, role="user"):
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def check_password(self, password):
        return check_password(password, self.password_hash)

    def get_info(self):
        return {"username": self.username, "role": self.role}


class Admin(User):
    def __init__(self, username, password_hash):
        super().__init__(username, password_hash, "admin")

    def create_user(self):
        username = input("Enter new username: ").strip()
        password = input("Enter password: ").strip()
        role = input("Select role (doctor/nurse): ").lower().strip()

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


class Doctor(User):
    def __init__(self, username, password_hash):
        super().__init__(username, password_hash, "doctor")


class Nurse(User):
    def __init__(self, username, password_hash):
        super().__init__(username, password_hash, "nurse")


class UserFactory:
    @staticmethod
    def create_user_object(username, password_hash, role):
        if role == "admin":
            return Admin(username, password_hash)
        elif role == "doctor":
            return Doctor(username, password_hash)
        elif role == "nurse":
            return Nurse(username, password_hash)
        else:
            return User(username, password_hash, role)


def login():
    global _current_user
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    users = read_users()

    for u in users:
        user_obj = UserFactory.create_user_object(u["username"], u["passwordHash"], u["role"])
        if user_obj.username == username and user_obj.check_password(password):
            _current_user = user_obj
            print(f"SUCCESS: Logged in as {username} ({user_obj.role})")
            logs = read_logs()
            logs.append({"username": username, "role": user_obj.role,
                         "loggedinAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            write_logs(logs)
            return

    print("ERROR: Invalid credentials")


def logout():
    global _current_user
    if _current_user:
        print(f"SUCCESS: User '{_current_user.username}' logged out")
        _current_user = None
    else:
        print("INFO: No user currently logged in")


def get_current_user():
    return _current_user
