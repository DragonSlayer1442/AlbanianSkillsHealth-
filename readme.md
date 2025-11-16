# Health+ CLI

Health+ CLI is a command-line interface for managing patients, reports, and doctor workflows. It allows user authentication, patient creation, report uploading, fuzzy matching of reports to patients, searching patients, and a doctor dashboard.

---

## Features

### User Management
- Login and logout
- Role-based access: `admin`, `doctor`, `nurse`
- Admin can create new users

### Patient Management
- Create patients (doctors only)
- Store patient data with MRN, name, DOB, assigned doctor, and transmissions
- Normalize patient identifiers for matching

### Report Management
- Upload HL7 or PDF reports
- Exact and fuzzy matching of reports to patients
- View matched report transmissions

### Doctor Dashboard
- View list of assigned patients
- View patient details and transmissions
- Search patients by name or MRN

### Search
- Case-insensitive
- Partial name or MRN matches
- Automatic display if a single match is found
- Multiple matches allow selection

---

## Project Structure

