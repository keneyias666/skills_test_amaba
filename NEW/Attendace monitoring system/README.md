# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 06
## Employee Attendance & Payroll Monitoring System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-ATT-06`
- **Course / Module:** Web Systems Development & Relational Database Applications
- **Allowed Time:** 3 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
*Apex Corporate Logistics Inc.* requires a reliable, locally deployed Employee Attendance and Payroll Monitoring web application. The company operates multiple operational departments (Accounting, Warehouse, HR, IT, Production, Marketing) and employs staff at distinct hourly rates.

Previously, attendance was tracked via manual log sheets, causing payroll discrepancies, unverified hours, and accidental deletion of attendance history.

As the software engineer taking this skills test, **you are tasked to implement, verify, and document the complete web application** that manages Departments, Employees, and Daily Time Records (DTR), with automated working hour calculation and payroll reporting.

---

## 2. System Architecture & Directory Layout

```text
NEW/Attendace monitoring system/
├── app.py              # Main Flask application with controllers & business logic
├── dbhelper.py         # Dedicated SQLite database helper functions
├── Attendance.db       # SQLite database file (auto-generated)
├── requirements.txt    # Project Python dependencies
├── static/
│   └── style.css       # Clean corporate UI styling
└── templates/
    ├── base.html             # Master layout with navigation bar
    ├── index.html            # Main navigation dashboard
    ├── departments.html      # Department listing
    ├── department_form.html  # Department add/edit form
    ├── employees.html        # Employee roster with department join
    ├── employee_form.html    # Employee add/edit form
    ├── attendance.html       # Attendance logs table
    ├── attendance_form.html  # Clock-in / clock-out logging form
    ├── monitoring.html       # Monitoring report selection hub
    ├── monitor_employee.html # Individual employee DTR & pay summary
    └── monitor_range.html    # Date-range attendance & hours audit
```

---

## 3. Database Specification & Data Dictionary

Your database must be stored in `Attendance.db`. You must enforce relational foreign keys (`PRAGMA foreign_keys = ON;`).

### Table 1: `Departments`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `depCode` | INTEGER | PRIMARY KEY | Unique department identifier (e.g. 10, 11) |
| `depName` | TEXT | NOT NULL | Department Name (e.g. "Accounting") |
| `depHead` | TEXT | NOT NULL | Department Head full name |
| `depTelNo` | TEXT | NOT NULL | Department contact telephone extension |

### Table 2: `Employees`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `empID` | INTEGER | PRIMARY KEY | Unique employee number (e.g. 225) |
| `deptCode` | INTEGER | NOT NULL, FK | References `Departments(depCode)` |
| `empName` | TEXT | NOT NULL | Employee first name |
| `empLName` | TEXT | NOT NULL | Employee last name |
| `empRateHr` | REAL | NOT NULL, CHECK(`empRateHr >= 0`) | Hourly pay rate in PHP (₱) |

### Table 3: `Attendance`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `attRN` | INTEGER | PRIMARY KEY AUTOINCREMENT | Attendance Record Number |
| `empID` | INTEGER | NOT NULL, FK | References `Employees(empID)` |
| `attDate` | TEXT | NOT NULL | Attendance Date (`YYYY-MM-DD`) |
| `attTimeIn` | TEXT | NOT NULL | Clock-in stamp (`YYYY-MM-DD HH:MM`) |
| `attTimeOut` | TEXT | NOT NULL | Clock-out stamp (`YYYY-MM-DD HH:MM`) |
| `attStat` | TEXT | NOT NULL, DEFAULT `'Not'` | Status: `'Not'` (Active) or `'Cancelled'` |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Database Setup & Data Integrity (20 Points)
- [ ] **Task 1.1 — Schema & Relations:** Initialize all three tables (`Departments`, `Employees`, `Attendance`) with exact primary keys, foreign keys, and CHECK constraints.
- [ ] **Task 1.2 — Foreign Key Enforcement:** Ensure every database connection executes `PRAGMA foreign_keys = ON;`.
- [ ] **Task 1.3 — Baseline Seeding:** Pre-seed the system with at least 6 standard departments and initial employee records when the database is empty.
- [ ] **Task 1.4 — Safe Deletion Guard:** Prevent deleting a department if employees belong to it; prevent deleting an employee if attendance rows reference them.

### Part 2: Department & Employee Management (25 Points)
- [ ] **Task 2.1 — Department CRUD:** Implement routes to view all departments (`/departments`), add new department (`/departments/add`), edit existing details (`/departments/<depCode>/edit`), and delete (`/departments/<depCode>/delete`).
- [ ] **Task 2.2 — Duplicate Code Prevention:** Validate that `depCode` is positive and not already taken before insertion.
- [ ] **Task 2.3 — Employee CRUD & JOIN Query:** Implement employee listing (`/employees`) using an `INNER JOIN` to fetch the human-readable `depName`.
- [ ] **Task 2.4 — Wage Validation:** Validate that `empRateHr` is a non-negative float and formatted to 2 decimal places.

### Part 3: Attendance Logging & Status Control (25 Points)
- [ ] **Task 3.1 — Time Recording Form:** Provide a form (`/attendance/record`) allowing selection of active employees, date, time-in, and time-out.
- [ ] **Task 3.2 — Time Logic Validation:** Verify that `Time Out` is strictly greater than `Time In`. If user inputs an invalid timestamp or inverted time, display a friendly flash alert.
- [ ] **Task 3.3 — Soft Cancellation (No Data Loss):** When an admin cancels a record via `/attendance/<attRN>/cancel`, update `attStat = 'Cancelled'`. Do NOT hard-delete from the database.

### Part 4: Payroll Monitoring & Reporting (20 Points)
- [ ] **Task 4.1 — Hours Worked Calculation:** Compute hours using:
  $$\text{Hours} = \frac{\text{TimeOut} - \text{TimeIn}}{3600 \text{ seconds}}$$
  Exclude any records where `attStat == 'Cancelled'`.
- [ ] **Task 4.2 — Individual Employee Summary (`/monitoring/employee`):** Look up an employee by `empID`, display their valid attendance history, sum their total rendered hours, and calculate gross salary:
  $$\text{Gross Salary} = \text{Total Hours} \times \text{empRateHr}$$
- [ ] **Task 4.3 — Date-Range Audit (`/monitoring/range`):** Allow HR to specify `date_from` and `date_to` and display all valid shifts and cumulative hours in that window.

### Part 5: UI Presentation & Quality (10 Points)
- [ ] **Task 5.1 — Currency & Date Formatters:** Implement Jinja custom filters `|money` (e.g. `₱500.00`) and `|when` (e.g. `4/15/24 8:20AM`).
- [ ] **Task 5.2 — Flash Messaging:** Show clear success/error flash banners on all form submissions.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Database Architecture** | Correct schema, foreign keys, CHECK constraints, seed data, no orphan records | 20 pts |
| **Department & Employee Modules** | Full CRUD, join queries, duplicate detection, input sanitation | 25 pts |
| **Attendance Operations** | Correct time parsing, logical validation, soft cancellation | 25 pts |
| **Payroll & Reports** | Precise hours computation, correct salary calculation, date range filter | 20 pts |
| **UI, Jinja & Formatting** | Jinja filters, clear navigation, flash feedback, clean styling | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Activate Virtual Environment & Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Application:**
   ```bash
   python app.py
   ```
3. **Open Browser:**
   Navigate to `http://127.0.0.1:5000`
4. **Sample Test Flow:**
   - Go to **Departments**: Verify Accounting, Warehouse, etc.
   - Go to **Employees**: Add a new employee with ID `301`, Rate `₱450.00`.
   - Go to **Attendance**: Record 08:00 to 17:00 (9.0 hours).
   - Go to **Monitoring**: Search for employee `301`. Verify total hours = `9.00` and pay = `₱4,050.00`.
