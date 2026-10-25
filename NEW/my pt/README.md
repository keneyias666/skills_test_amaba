# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 05
## Veterinary Clinic & Pet Consultation System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-PET-05`
- **Course / Module:** Relational Healthcare Information Systems & Clinical Workflows
- **Allowed Time:** 3 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, W3.CSS

---

## 1. Scenario & Problem Statement
*St. Francis Veterinary Hospital & Animal Care Center* requires an integrated clinical management web application. The hospital manages pet owners, their registered animal patients, attending veterinarians, and detailed medical consultation logs.

To comply with veterinary medical compliance standards:
1. Medical and patient records must **never be permanently erased**; any deletion must be a logical soft-delete (`is_deleted = 1`).
2. Consultations must record date, 12-hour AM/PM times parsed into standardized 24-hour format, clinical diagnosis, and prescribed medication.
3. The administration requires a multi-criteria **Clinical Inquiry & Analytics Engine** capable of filtering records by veterinarian specialization, pet species, owner, and consultation date.

As the examinee, **you must implement and verify the entire clinical data pipeline and multi-criteria inquiry engine**.

---

## 2. System Architecture & Directory Layout

```text
NEW/my pt/
├── pet.py              # Main Flask application and clinical routing
├── dbhelper.py         # Database CRUD helper functions
├── database.py         # SQLite schema initialization and connection manager
├── clinic.db           # SQLite database file
├── sqlite3.exe         # Local SQLite CLI
└── templates/
    ├── base.html              # W3.CSS clinical layout with navbar
    ├── index.html             # Clinic overview dashboard
    ├── login.html / signup.html # Authentication
    ├── owners.html / owner_form.html # Pet owner registry
    ├── pets.html / pet_form.html     # Pet patient registry
    ├── vets.html / vet_form.html     # Veterinarian staff registry
    ├── consultations.html     # Clinical consultation logs
    ├── consultation_form.html # Consultation appointment logging
    ├── inquiry.html           # Multi-criteria clinical search engine
    ├── raffle.html            # Promotional raffle draw module
    ├── report_summary.html    # Clinical volume summary
    └── report_by_campus.html  # Multi-location distribution report
```

---

## 3. Database Specification & Data Dictionary

Database path: `clinic.db`
All tables implement soft deletion: `is_deleted INTEGER NOT NULL DEFAULT 0`.
Enforce foreign keys: `PRAGMA foreign_keys = ON;`.

### Table 1: `PetOwner`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `petOwnerID` | TEXT | PRIMARY KEY | Unique Owner Code (e.g. `OWN-001`) |
| `ownerFName` | TEXT | NOT NULL | Owner first name |
| `ownerLName` | TEXT | NOT NULL | Owner last name |
| `ownerAddress` | TEXT | NOT NULL | Residential address |
| `ownerContact` | TEXT | NOT NULL | Phone contact number |
| `is_deleted` | INTEGER | NOT NULL, DEFAULT 0 | Soft delete flag |

### Table 2: `Veterinarian`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `vetID` | TEXT | PRIMARY KEY | Unique Veterinarian Code |
| `vetFName` | TEXT | NOT NULL | Veterinarian first name |
| `vetLName` | TEXT | NOT NULL | Veterinarian last name |
| `vetContact` | TEXT | NOT NULL | Mobile / Pager number |
| `specialization` | TEXT | NOT NULL | Specialization (e.g. "Surgery", "Feline") |
| `is_deleted` | INTEGER | NOT NULL, DEFAULT 0 | Soft delete flag |

### Table 3: `Pet`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `petID` | TEXT | PRIMARY KEY | Unique Pet ID |
| `petName` | TEXT | NOT NULL | Pet Name |
| `petType` | TEXT | NOT NULL | Species (e.g. "Canine", "Feline") |
| `petBreed` | TEXT | NOT NULL | Breed |
| `petBDate` | TEXT | NOT NULL | Birthdate (`YYYY-MM-DD`) |
| `petOwnerID` | TEXT | NOT NULL, FK | References `PetOwner(petOwnerID)` |
| `is_deleted` | INTEGER | NOT NULL, DEFAULT 0 | Soft delete flag |

### Table 4: `Consultation`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `consultID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Consultation Record ID |
| `petID` | TEXT | NOT NULL, FK | References `Pet(petID)` |
| `vetID` | TEXT | NOT NULL, FK | References `Veterinarian(vetID)` |
| `consultDate`| TEXT | NOT NULL | Date (`YYYY-MM-DD`) |
| `consultTime`| TEXT | NOT NULL | Standard 24h Time (`HH:MM`) |
| `diagnosis` | TEXT | NOT NULL | Clinical findings |
| `treatment` | TEXT | NOT NULL | Prescription / Medical plan |
| `is_deleted` | INTEGER | NOT NULL, DEFAULT 0 | Soft delete flag |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Schema Setup & Logical Deletion in `database.py` (20 Points)
- [ ] **Task 1.1 — Schema Definition:** Create all four tables with foreign keys and `is_deleted DEFAULT 0`.
- [ ] **Task 1.2 — Soft Deletion Query Pattern:** Ensure every query (SELECT, UPDATE, DELETE) respects the `is_deleted` flag:
  - SELECT: `WHERE is_deleted = 0`
  - DELETE: `UPDATE <table> SET is_deleted = 1 WHERE ...`

### Part 2: Pet Owner & Veterinarian Management (25 Points)
- [ ] **Task 2.1 — Pet Owner CRUD (`/owners`):** Implement listing, adding, editing, and soft-deleting pet owners.
- [ ] **Task 2.2 — Veterinarian CRUD (`/vets`):** Implement full veterinarian records with medical specialization.
- [ ] **Task 2.3 — Duplicate Prevention:** Catch unique ID violations gracefully with user-friendly flash messages.

### Part 3: Pet Patient Registry & Date Validation (25 Points)
- [ ] **Task 3.1 — Pet CRUD (`/pets`):** Relate each pet to an existing pet owner using a `<select>` dropdown.
- [ ] **Task 3.2 — Biological Date Check:** Validate that `petBDate` is in valid `YYYY-MM-DD` format and is **not in the future** (`petBDate <= today`).

### Part 4: Clinical Consultations & Time Conversion (20 Points)
- [ ] **Task 4.1 — Time Conversion:**
  Accept user input in 12-hour AM/PM format (e.g. `02:30 PM`) and standardize into 24-hour format (`14:30`) for database storage.
- [ ] **Task 4.2 — Consultation Logging (`/consultations`):**
  Record consultation linking Pet, Attending Vet, Date/Time, Diagnosis, and Treatment.
- [ ] **Task 4.3 — Multi-Criteria Inquiry Engine (`/inquiry`):**
  Support filtering consultations by:
  1. Attending Veterinarian
  2. Pet Species / Type
  3. Pet Owner Name
  4. Specific Date Range

### Part 5: UI & UX Polish (10 Points)
- [ ] **Task 5.1 — W3.CSS Clean Theme:** Professional veterinary hospital styling.
- [ ] **Task 5.2 — Clear Feedback Alerts:** Flash messages on all successful operations and validation errors.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Database Architecture** | 4-table schema, foreign keys, soft deletion (`is_deleted = 0`) | 20 pts |
| **Owner & Vet CRUD** | Complete CRUD, ID validation, duplicate handling | 25 pts |
| **Pet Patient Registry** | Relational link to owner, future birthdate prevention | 25 pts |
| **Consultation & Inquiry** | 12h to 24h time conversion, diagnosis log, multi-criteria inquiry | 20 pts |
| **UI Presentation & Styling** | W3.CSS layout, flash alerts, clean form components | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Start the Flask Application:**
   ```bash
   python pet.py
   ```
2. **Access the Web Portal:**
   `http://127.0.0.1:5000/`
3. **Verification Steps:**
   - **Add Owner:** ID `OWN-01`, "Jane Doe", "Cebu City", "09123456789".
   - **Add Pet:** ID `PET-01`, "Buddy", "Canine", "Golden Retriever", Birthdate `2022-05-10`, Owner `OWN-01`.
   - **Future Date Test:** Attempt to set birthdate in 2030. Verify system blocks it.
   - **Add Vet:** ID `VET-01`, "Dr. Smith", "Surgery".
   - **Log Consultation:** Select Pet `Buddy`, Vet `Dr. Smith`, Time `02:30 PM`, Diagnosis "Routine checkup". Verify stored time is `14:30`.
   - **Inquiry Test:** Go to `/inquiry` and filter by Vet `Dr. Smith`. Verify Buddy's consultation appears.
   - **Soft Delete Test:** Delete `Buddy`. Verify Buddy is hidden from `/pets`, but remains in `clinic.db` with `is_deleted = 1`.
