from .user_management import login, logout, create_user
from .patient_management import create_patient
from parsing.report_uploader import upload_report

def run_cli():
    print("Welcome to Health+ CLI. Type 'help' to see commands.")
    while True:
        command = input("> ").strip().lower()
        if command == "help":
            print("Available commands:")
            print("login - Log in to the system")
            print("logout - Log out of the system")
            print("create-user - Admin only, create doctor/nurse account")
            print("create-patient - Doctors only, create patient record")
            print("upload-report - Doctors/Nurses only, upload HL7/PDF report")
            print("exit - Exit the CLI")
        elif command == "login":
            login()
        elif command == "logout":
            logout()
        elif command == "create-user":
            create_user()
        elif command == "create-patient":
            create_patient()
        elif command == "upload-report":
            upload_report()
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print("ERROR: Unknown command. Type 'help' to see available commands.")

