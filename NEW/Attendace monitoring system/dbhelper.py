"""
================================================================================
SKILLS TEST QUESTIONNAIRE: DATABASE HELPER MODULE (dbhelper.py)
System: Employee Attendance & Payroll Monitoring System
================================================================================
OBJECTIVE:
This module manages all database interactions (SQLite3) for the Employee
Attendance Monitoring System. Candidates taking this skills test must implement,
configure, and maintain database persistence across three relational entities:
Departments, Employees, and Attendance.

DATABASE ENTITIES:
1. Departments: (depCode PK, depName, depHead, depTelNo)
2. Employees:   (empID PK, deptCode FK, empName, empLName, empRateHr)
3. Attendance:  (attRN PK, empID FK, attDate, attTimeIn, attTimeOut, attStat)

CANDIDATE INSTRUCTIONS:
- Review each task below marked with `### SKILLS TEST TASK [X]`.
- Verify SQL queries, parameter bindings, constraints, and data return types.
================================================================================
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Path to the SQLite database
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "Attendance.db"

STATUS_NOT = "Not"
STATUS_CANCELLED = "Cancelled"


# ============================================================================
# ### SKILLS TEST TASK 1.1: DATABASE CONNECTION MANAGEMENT
# OBJECTIVE:
#   Create and return an active sqlite3 connection configured with foreign
#   keys enabled and Row factory for dictionary-like column access.
# WHAT NEEDS TO BE DONE:
#   1. Connect to DATABASE with a reasonable timeout (e.g. 10s).
#   2. Set `row_factory = sqlite3.Row`.
#   3. Execute `PRAGMA foreign_keys = ON;` to enforce relational integrity.
#   4. Return the connection object.
# ============================================================================
def get_connection():
    """Create and return a configured sqlite3 connection."""
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================================
# ### SKILLS TEST TASK 1.2: DATABASE SCHEMA & SEED DATA INITIALIZATION
# OBJECTIVE:
#   Define tables with relational integrity, check constraints, indexes,
#   and pre-populate baseline department, employee, and attendance records.
# WHAT NEEDS TO BE DONE:
#   1. Create `Departments` table if not exists with primary key `depCode`.
#   2. Create `Employees` table with foreign key to `Departments(depCode)` and
#      a CHECK constraint `empRateHr >= 0`.
#   3. Create `Attendance` table with foreign key to `Employees(empID)` and
#      status check `attStat IN ('Not', 'Cancelled')`.
#   4. Create performance indexes on `deptCode`, `empID`, and `attDate`.
#   5. Seed baseline data if tables are empty.
# ============================================================================
SCHEMA = """
CREATE TABLE IF NOT EXISTS Departments (
    depCode INTEGER PRIMARY KEY,
    depName TEXT NOT NULL,
    depHead TEXT NOT NULL,
    depTelNo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Employees (
    empID INTEGER PRIMARY KEY,
    deptCode INTEGER NOT NULL,
    empName TEXT NOT NULL,
    empLName TEXT NOT NULL,
    empRateHr REAL NOT NULL CHECK (empRateHr >= 0),
    FOREIGN KEY (deptCode) REFERENCES Departments (depCode)
);

CREATE TABLE IF NOT EXISTS Attendance (
    attRN INTEGER PRIMARY KEY AUTOINCREMENT,
    empID INTEGER NOT NULL,
    attDate TEXT NOT NULL,
    attTimeIn TEXT NOT NULL,
    attTimeOut TEXT NOT NULL,
    attStat TEXT NOT NULL DEFAULT 'Not' CHECK (attStat IN ('Not', 'Cancelled')),
    FOREIGN KEY (empID) REFERENCES Employees (empID)
);

CREATE INDEX IF NOT EXISTS idx_employees_dept ON Employees (deptCode);
CREATE INDEX IF NOT EXISTS idx_attendance_emp ON Attendance (empID);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON Attendance (attDate);
"""

DEPARTMENTS_SEED = [
    (10, "Accounting", "Caesar", "255111"),
    (11, "Warehouse", "Darwin", "255777"),
    (12, "HR", "Bernice", "255222"),
    (13, "IT", "Oliver", "255333"),
    (14, "Production", "Troy", "255444"),
    (15, "Marketing", "Jessica", "255555"),
]

EMPLOYEES_SEED = [
    (225, 11, "Hubert", "Fantino", 500.00),
    (226, 10, "Dene", "Duran", 450.00),
    (227, 15, "Jenner", "Anores", 500.00),
    (228, 15, "Catherine", "Carumba", 500.00),
    (229, 15, "Leah", "Suker", 445.00),
    (230, 14, "Leo", "Bermudez", 290.00),
]

ATTENDANCE_SEED = [
    (225, "2024-04-15", "2024-04-15 08:20", "2024-04-15 17:20", STATUS_NOT),
    (226, "2024-04-15", "2024-04-15 08:20", "2024-04-15 17:20", STATUS_NOT),
    (227, "2024-04-15", "2024-04-15 08:20", "2024-04-15 17:20", STATUS_NOT),
    (228, "2024-04-15", "2024-04-15 08:00", "2024-04-15 17:00", STATUS_NOT),
    (229, "2024-04-15", "2024-04-15 08:20", "2024-04-15 16:20", STATUS_NOT),
    (230, "2024-04-15", "2024-04-15 08:20", "2024-04-15 17:20", STATUS_NOT),
    (225, "2024-04-16", "2024-04-16 08:20", "2024-04-16 17:20", STATUS_NOT),
    (226, "2024-04-16", "2024-04-16 08:20", "2024-04-16 17:20", STATUS_NOT),
    (225, "2024-04-17", "2024-04-17 08:20", "2024-04-17 17:20", STATUS_NOT),
    (230, "2024-04-17", "2024-04-17 07:30", "2024-04-17 16:30", STATUS_NOT),
    (225, "2024-04-18", "2024-04-18 08:20", "2024-04-18 17:20", STATUS_CANCELLED),
]


def init_db():
    """Initialize database tables and default seed data."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Departments")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?, ?, ?, ?)",
                DEPARTMENTS_SEED,
            )
            cursor.executemany(
                "INSERT INTO Employees (empID, deptCode, empName, empLName, empRateHr) VALUES (?, ?, ?, ?, ?)",
                EMPLOYEES_SEED,
            )
            cursor.executemany(
                "INSERT INTO Attendance (empID, attDate, attTimeIn, attTimeOut, attStat) VALUES (?, ?, ?, ?, ?)",
                ATTENDANCE_SEED,
            )
            conn.commit()
    finally:
        conn.close()


# ============================================================================
# ### SKILLS TEST TASK 1.3: DEPARTMENT CRUD OPERATIONS
# OBJECTIVE:
#   Implement complete Create, Read, Update, and Delete operations for
#   Departments with integrity constraints preventing orphan employee records.
# WHAT NEEDS TO BE DONE:
#   - get_all_departments(): Return all department records ordered by depCode.
#   - get_department(dep_code): Return one department by primary key.
#   - add_department(code, name, head, tel): Insert new department.
#   - update_department(code, name, head, tel): Update department fields.
#   - delete_department(code): Check if employees exist before deleting;
#     raise ValueError or IntegrityError if department still has employees.
# ============================================================================

def get_all_departments():
    """Retrieve all departments ordered by department code."""
    conn = get_connection()
    try:
        return conn.execute("SELECT depCode, depName, depHead, depTelNo FROM Departments ORDER BY depCode").fetchall()
    finally:
        conn.close()


def get_department(dep_code):
    """Retrieve a single department by its primary key depCode."""
    conn = get_connection()
    try:
        return conn.execute("SELECT depCode, depName, depHead, depTelNo FROM Departments WHERE depCode = ?", (dep_code,)).fetchone()
    finally:
        conn.close()


def add_department(dep_code, dep_name, dep_head, dep_tel_no):
    """Insert a new department into the database."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?, ?, ?, ?)",
            (dep_code, dep_name, dep_head, dep_tel_no),
        )
        conn.commit()
    finally:
        conn.close()


def update_department(dep_code, dep_name, dep_head, dep_tel_no):
    """Update department information by depCode."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE Departments SET depName = ?, depHead = ?, depTelNo = ? WHERE depCode = ?",
            (dep_name, dep_head, dep_tel_no, dep_code),
        )
        conn.commit()
    finally:
        conn.close()


def delete_department(dep_code):
    """Delete a department. Prevents deletion if employees are assigned."""
    conn = get_connection()
    try:
        # Check relational dependency
        in_use = conn.execute("SELECT 1 FROM Employees WHERE deptCode = ?", (dep_code,)).fetchone()
        if in_use:
            raise ValueError("This department still has employees and cannot be deleted.")
        conn.execute("DELETE FROM Departments WHERE depCode = ?", (dep_code,))
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# ### SKILLS TEST TASK 1.4: EMPLOYEE CRUD OPERATIONS & JOINS
# OBJECTIVE:
#   Implement Employee management including relational JOIN with Departments
#   to fetch the department name alongside employee details.
# WHAT NEEDS TO BE DONE:
#   - get_all_employees(): Return all employees JOINed with Departments.
#   - get_employee(emp_id): Fetch single employee by ID.
#   - add_employee(emp_id, dept_code, first_name, last_name, rate): Insert employee.
#   - update_employee(emp_id, dept_code, first_name, last_name, rate): Update info.
#   - delete_employee(emp_id): Disallow deletion if attendance records exist.
# ============================================================================

def get_all_employees():
    """Retrieve all employees joined with their corresponding department name."""
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT e.empID, e.deptCode, e.empName, e.empLName, e.empRateHr, d.depName
            FROM Employees e
            JOIN Departments d ON d.depCode = e.deptCode
            ORDER BY e.empID
        """).fetchall()
    finally:
        conn.close()


def get_employee(emp_id):
    """Retrieve an employee by primary key empID."""
    conn = get_connection()
    try:
        return conn.execute("SELECT empID, deptCode, empName, empLName, empRateHr FROM Employees WHERE empID = ?", (emp_id,)).fetchone()
    finally:
        conn.close()


def add_employee(emp_id, dept_code, first_name, last_name, rate_hr):
    """Add a new employee record."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Employees (empID, deptCode, empName, empLName, empRateHr) VALUES (?, ?, ?, ?, ?)",
            (emp_id, dept_code, first_name, last_name, rate_hr),
        )
        conn.commit()
    finally:
        conn.close()


def update_employee(emp_id, dept_code, first_name, last_name, rate_hr):
    """Update employee details by empID."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE Employees SET deptCode = ?, empName = ?, empLName = ?, empRateHr = ? WHERE empID = ?",
            (dept_code, first_name, last_name, rate_hr, emp_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_employee(emp_id):
    """Delete an employee if no attendance logs are linked."""
    conn = get_connection()
    try:
        in_use = conn.execute("SELECT 1 FROM Attendance WHERE empID = ?", (emp_id,)).fetchone()
        if in_use:
            raise ValueError("This employee has attendance records and cannot be deleted.")
        conn.execute("DELETE FROM Employees WHERE empID = ?", (emp_id,))
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# ### SKILLS TEST TASK 1.5: ATTENDANCE LOGGING & SOFT-STATUS CANCELLATION
# OBJECTIVE:
#   Log employee time-in and time-out with status 'Not' (active/valid).
#   Implement soft-status cancellation ('Cancelled') instead of hard delete.
# WHAT NEEDS TO BE DONE:
#   - record_attendance(emp_id, date, time_in, time_out): Insert attendance row.
#   - cancel_attendance(att_rn): Update status to 'Cancelled' where status is 'Not'.
#   - get_active_attendance_by_employee(emp_id): Fetch valid records for payroll.
#   - get_active_attendance_by_date_range(start_date, end_date): Filter date range.
# ============================================================================

def record_attendance(emp_id, att_date, time_in, time_out):
    """Insert a new attendance log with default status 'Not'."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Attendance (empID, attDate, attTimeIn, attTimeOut, attStat) VALUES (?, ?, ?, ?, ?)",
            (emp_id, att_date, time_in, time_out, STATUS_NOT),
        )
        conn.commit()
    finally:
        conn.close()


def cancel_attendance(att_rn):
    """Cancel an active attendance log (soft status update)."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE Attendance SET attStat = ? WHERE attRN = ? AND attStat = ?",
            (STATUS_CANCELLED, att_rn, STATUS_NOT),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_attendance():
    """Fetch all attendance records ordered by record number."""
    conn = get_connection()
    try:
        return conn.execute("SELECT attRN, empID, attDate, attTimeIn, attTimeOut, attStat FROM Attendance ORDER BY attRN").fetchall()
    finally:
        conn.close()


def get_employee_attendance(emp_id):
    """Fetch all active ('Not' cancelled) attendance rows for an employee."""
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT attRN, empID, attDate, attTimeIn, attTimeOut
            FROM Attendance
            WHERE attStat = ? AND empID = ?
            ORDER BY attDate, attTimeIn
        """, (STATUS_NOT, emp_id)).fetchall()
    finally:
        conn.close()


def get_range_attendance(start_date, end_date):
    """Fetch active attendance rows within a date range (inclusive)."""
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT attRN, empID, attDate, attTimeIn, attTimeOut
            FROM Attendance
            WHERE attStat = ? AND attDate >= ? AND attDate <= ?
            ORDER BY attDate, attTimeIn
        """, (STATUS_NOT, start_date, end_date)).fetchall()
    finally:
        conn.close()
