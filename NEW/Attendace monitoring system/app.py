# ============================================================================
# SKILLS TEST QUESTIONNAIRE: EMPLOYEE ATTENDANCE & PAYROLL MONITORING SYSTEM
# ============================================================================
# EXAM SCENARIO:
#   A company needs a centralized Attendance and Payroll Hours Tracking system.
#   Human Resources logs employee Daily Time Records (DTR), calculates hours worked,
#   tracks hourly billing rates, and generates payroll and audit summary reports.
#
# CANDIDATE TASKS & OBJECTIVES (WHAT NEEDS TO BE DONE):
#   1. DATABASE ARCHITECTURE:
#      - Enforce relational constraints across Departments, Employees, and Attendance.
#      - Ensure foreign keys are enabled (PRAGMA foreign_keys = ON).
#      - Check that hourly rates cannot be negative (empRateHr >= 0).
#   2. CRUD CONTROLLERS & ROUTES:
#      - Department Management (/departments, /departments/add, edit, delete).
#      - Employee Onboarding (/employees, /employees/add, edit, delete).
#      - Attendance Time Records (/attendance, /attendance/record, cancel).
#   3. VALIDATIONS & CALCULATIONS:
#      - Validate that Time Out is strictly after Time In on the same date.
#      - Calculate hours worked using timestamp difference / 3600.
#      - Compute gross payroll: Rate Per Hour * Total Hours Worked.
#      - Soft-cancel attendance records (attStat = 'Cancelled') without data loss.
#   4. REPORTING & FILTERING:
#      - Monitor individual employee attendance history with total pay.
#      - Monitor departmental and range attendance by date filters.
# ============================================================================

import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "Attendance.db"

STATUS_NOT = "Not"
STATUS_CANCELLED = "Cancelled"

app = Flask(__name__)
app.config["SECRET_KEY"] = "attendance-local-admin"

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
    attRN INTEGER PRIMARY KEY,
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

DEPARTMENTS = [
    (10, "Accounting", "Caesar", "255111"),
    (11, "Warehouse", "Darwin", "255777"),
    (12, "HR", "Bernice", "255222"),
    (13, "IT", "Oliver", "255333"),
    (14, "Production", "Troy", "255444"),
    (15, "Marketing", "Jessica", "255555"),
]

# empID, deptCode, first name, last name, rate per hour
EMPLOYEES = [
    (225, 11, "Hubert", "Fantino", 500.00),
    (226, 10, "Dene", "Duran", 450.00),
    (227, 15, "Jenner", "Anores", 500.00),
    (228, 15, "Catherine", "Carumba", 500.00),
    (229, 15, "Leah", "Suker", 445.00),
    (230, 14, "Leo", "Bermudez", 290.00),
]

# One cancelled row is included so the recording screen can show that status.
ATTENDANCE = [
    (1, 225, "2024-04-15", "08:20", "17:20", STATUS_NOT),
    (2, 226, "2024-04-15", "08:20", "17:20", STATUS_NOT),
    (3, 227, "2024-04-15", "08:20", "17:20", STATUS_NOT),
    (4, 228, "2024-04-15", "08:00", "17:00", STATUS_NOT),
    (5, 229, "2024-04-15", "08:20", "16:20", STATUS_NOT),
    (6, 230, "2024-04-15", "08:20", "17:20", STATUS_NOT),
    (7, 225, "2024-04-16", "08:20", "17:20", STATUS_NOT),
    (8, 226, "2024-04-16", "08:20", "17:20", STATUS_NOT),
    (9, 225, "2024-04-17", "08:20", "17:20", STATUS_NOT),
    (10, 230, "2024-04-17", "07:30", "16:30", STATUS_NOT),
    (11, 225, "2024-04-18", "08:20", "17:20", STATUS_CANCELLED),
]


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DATABASE, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def seed(conn):
    conn.executemany(
        "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?, ?, ?, ?)",
        DEPARTMENTS,
    )
    conn.executemany(
        """
        INSERT INTO Employees (empID, deptCode, empName, empLName, empRateHr)
        VALUES (?, ?, ?, ?, ?)
        """,
        EMPLOYEES,
    )
    conn.executemany(
        """
        INSERT INTO Attendance (attRN, empID, attDate, attTimeIn, attTimeOut, attStat)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (rn, emp_id, day, f"{day} {time_in}", f"{day} {time_out}", status)
            for rn, emp_id, day, time_in, time_out, status in ATTENDANCE
        ],
    )


def init_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        empty = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM Departments) = 0
                AND (SELECT COUNT(*) FROM Employees) = 0
                AND (SELECT COUNT(*) FROM Attendance) = 0
            """
        ).fetchone()[0]
        if empty:
            seed(conn)
            conn.commit()
    finally:
        conn.close()


def require_text(value, label, limit=60):
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} is required.")
    if len(text) > limit:
        raise ValueError(f"{label} must be {limit} characters or fewer.")
    return text


def parse_int(value, label):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be a whole number.") from None
    if number <= 0:
        raise ValueError(f"{label} must be greater than zero.")
    if number > 1_000_000:
        raise ValueError(f"{label} is too large.")
    return number


def parse_rate(value):
    try:
        rate = round(float(str(value).strip()), 2)
    except (TypeError, ValueError):
        raise ValueError("Rate per hour must be a number.") from None
    if rate < 0:
        raise ValueError("Rate per hour cannot be negative.")
    if rate > 1_000_000:
        raise ValueError("Rate per hour is too large.")
    return rate


def parse_clock(date_text, time_text):
    for pattern in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(f"{date_text} {time_text}", pattern)
        except ValueError:
            continue
    raise ValueError


def build_attendance_times(date_text, time_in_text, time_out_text):
    date_text = (date_text or "").strip()
    time_in_text = (time_in_text or "").strip()
    time_out_text = (time_out_text or "").strip()
    try:
        day = datetime.strptime(date_text, "%Y-%m-%d")
        start = parse_clock(date_text, time_in_text)
        end = parse_clock(date_text, time_out_text)
    except ValueError:
        raise ValueError("Enter a valid date, time in, and time out.") from None
    if end <= start:
        raise ValueError("Time out must be later than time in.")
    return (
        day.strftime("%Y-%m-%d"),
        start.strftime("%Y-%m-%d %H:%M"),
        end.strftime("%Y-%m-%d %H:%M"),
    )


def parse_date(value, label):
    try:
        return datetime.strptime((value or "").strip(), "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{label} must be a valid date.") from None


def format_dt(value):
    if not value:
        return ""
    try:
        stamp = datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return value
    hour = stamp.hour % 12 or 12
    suffix = "AM" if stamp.hour < 12 else "PM"
    return f"{stamp.month}/{stamp.day}/{stamp.strftime('%y')} {hour}:{stamp.minute:02d}{suffix}"


def format_day(value):
    stamp = value if isinstance(value, datetime) else datetime.strptime(value, "%Y-%m-%d")
    return f"{stamp.month}/{stamp.day}/{stamp.year}"


def hours_between(time_in, time_out):
    start = datetime.strptime(time_in, "%Y-%m-%d %H:%M")
    end = datetime.strptime(time_out, "%Y-%m-%d %H:%M")
    return round((end - start).total_seconds() / 3600, 2)


def with_hours(rows):
    records = []
    total = 0.0
    for row in rows:
        item = dict(row)
        item["hours"] = hours_between(item["attTimeIn"], item["attTimeOut"])
        total += item["hours"]
        records.append(item)
    return records, round(total, 2)


def today_text():
    today = datetime.now()
    return f"{today.month}/{today.day}/{today.year}"


def next_number(table, column):
    row = get_db().execute(
        f"SELECT COALESCE(MAX({column}), 0) + 1 AS n FROM {table}"
    ).fetchone()
    return row["n"]


@app.template_filter("when")
def when_filter(value):
    return format_dt(value)


@app.template_filter("money")
def money_filter(value):
    return f"₱{float(value):,.2f}"


@app.route("/")
def menu():
    return render_template("index.html")


# ============================================================================
# ### SKILLS TEST TASK 2.1: LIST ALL DEPARTMENTS
# OBJECTIVE: Fetch all departments sorted numerically by depCode and render
# the departments list template.
# WHAT NEEDS TO BE DONE:
#   1. Query: SELECT depCode, depName, depHead, depTelNo FROM Departments ORDER BY depCode
#   2. Pass rows into render_template("departments.html", departments=rows)
# ============================================================================
@app.route("/departments")
def departments():
    rows = get_db().execute(
        "SELECT depCode, depName, depHead, depTelNo FROM Departments ORDER BY depCode"
    ).fetchall()
    return render_template("departments.html", departments=rows)


def render_department_form(department=None):
    suggested = None if department else next_number("Departments", "depCode")
    return render_template(
        "department_form.html",
        department=department,
        suggested=suggested,
    )


# ============================================================================
# ### SKILLS TEST TASK 2.2: ADD NEW DEPARTMENT
# OBJECTIVE: Validate input fields, verify code uniqueness, and insert a new department.
# WHAT NEEDS TO BE DONE:
#   1. GET: Render empty department form with an auto-suggested next code.
#   2. POST:
#      - Extract: depCode (integer), depName (text), depHead (text), depTelNo (text).
#      - Validation: Ensure all fields are filled; check if depCode already exists.
#      - Query: INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?, ?, ?, ?)
#      - Flash success message and redirect to /departments.
# ============================================================================
@app.route("/departments/add", methods=["GET", "POST"])
def add_department():
    if request.method == "POST":
        try:
            dep_code = parse_int(request.form.get("depCode"), "Department code")
            dep_name = require_text(request.form.get("depName"), "Department name")
            dep_head = require_text(request.form.get("depHead"), "Department head")
            dep_tel = require_text(request.form.get("depTelNo"), "Telephone number", 20)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_department_form()

        db = get_db()
        taken = db.execute(
            "SELECT 1 FROM Departments WHERE depCode = ?",
            (dep_code,),
        ).fetchone()
        if taken:
            flash("That department code is already used.", "error")
            return render_department_form()

        db.execute(
            "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?, ?, ?, ?)",
            (dep_code, dep_name, dep_head, dep_tel),
        )
        db.commit()
        flash("Department saved.", "success")
        return redirect(url_for("departments"))

    return render_department_form()


# ============================================================================
# ### SKILLS TEST TASK 2.3: EDIT DEPARTMENT
# OBJECTIVE: Fetch existing department by code, display in form, and update on POST.
# WHAT NEEDS TO BE DONE:
#   1. Lookup department by depCode. If None, flash error and redirect to /departments.
#   2. POST: Validate updated depName, depHead, depTelNo.
#   3. Query: UPDATE Departments SET depName = ?, depHead = ?, depTelNo = ? WHERE depCode = ?
#   4. Commit changes, flash "Department updated.", and redirect to /departments.
# ============================================================================
@app.route("/departments/<int:dep_code>/edit", methods=["GET", "POST"])
def edit_department(dep_code):
    db = get_db()
    department = db.execute(
        "SELECT depCode, depName, depHead, depTelNo FROM Departments WHERE depCode = ?",
        (dep_code,),
    ).fetchone()
    if department is None:
        flash("Department not found.", "error")
        return redirect(url_for("departments"))

    if request.method == "POST":
        try:
            dep_name = require_text(request.form.get("depName"), "Department name")
            dep_head = require_text(request.form.get("depHead"), "Department head")
            dep_tel = require_text(request.form.get("depTelNo"), "Telephone number", 20)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_department_form(department)

        db.execute(
            "UPDATE Departments SET depName = ?, depHead = ?, depTelNo = ? WHERE depCode = ?",
            (dep_name, dep_head, dep_tel, dep_code),
        )
        db.commit()
        flash("Department updated.", "success")
        return redirect(url_for("departments"))

    return render_department_form(department)


# ============================================================================
# ### SKILLS TEST TASK 2.4: DELETE DEPARTMENT (SAFE REMOVAL GUARD)
# OBJECTIVE: Prevent orphan employee records by checking if employees exist
# in the department before deleting.
# WHAT NEEDS TO BE DONE:
#   1. Check if department exists. If not, redirect with error.
#   2. Check: SELECT 1 FROM Employees WHERE deptCode = ?
#   3. If employees found, BLOCK deletion: flash error and redirect.
#   4. Otherwise, execute: DELETE FROM Departments WHERE depCode = ?
#   5. Commit transaction, flash success, and redirect to /departments.
# ============================================================================
@app.route("/departments/<int:dep_code>/delete", methods=["POST"])
def delete_department(dep_code):
    db = get_db()
    department = db.execute(
        "SELECT depCode FROM Departments WHERE depCode = ?",
        (dep_code,),
    ).fetchone()
    if department is None:
        flash("Department not found.", "error")
        return redirect(url_for("departments"))

    in_use = db.execute(
        "SELECT 1 FROM Employees WHERE deptCode = ?",
        (dep_code,),
    ).fetchone()
    if in_use:
        flash("This department still has employees and cannot be deleted.", "error")
        return redirect(url_for("departments"))

    try:
        db.execute("DELETE FROM Departments WHERE depCode = ?", (dep_code,))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        flash("This department still has employees and cannot be deleted.", "error")
        return redirect(url_for("departments"))

    flash("Department deleted.", "success")
    return redirect(url_for("departments"))


# ============================================================================
# ### SKILLS TEST TASK 3.1: LIST ALL EMPLOYEES (RELATIONAL JOIN)
# OBJECTIVE: Retrieve all employees with their human-readable department name
# via an INNER JOIN on Departments.
# WHAT NEEDS TO BE DONE:
#   1. Query:
#      SELECT e.empID, e.deptCode, e.empName, e.empLName, e.empRateHr, d.depName
#      FROM Employees e
#      JOIN Departments d ON d.depCode = e.deptCode
#      ORDER BY e.empID
#   2. Pass rows into render_template("employees.html", employees=rows)
# ============================================================================
@app.route("/employees")
def employees():
    rows = get_db().execute(
        """
        SELECT e.empID, e.deptCode, e.empName, e.empLName, e.empRateHr, d.depName
        FROM Employees e
        JOIN Departments d ON d.depCode = e.deptCode
        ORDER BY e.empID
        """
    ).fetchall()
    return render_template("employees.html", employees=rows)


def department_choices():
    return get_db().execute(
        "SELECT depCode, depName FROM Departments ORDER BY depCode"
    ).fetchall()


def render_employee_form(employee=None):
    suggested = None if employee else next_number("Employees", "empID")
    return render_template(
        "employee_form.html",
        employee=employee,
        departments=department_choices(),
        suggested=suggested,
    )


# ============================================================================
# ### SKILLS TEST TASK 3.2: ADD NEW EMPLOYEE
# OBJECTIVE: Validate employee inputs, verify unique empID, check valid deptCode,
# and insert new record into Employees.
# WHAT NEEDS TO BE DONE:
#   1. Check that at least one department exists.
#   2. POST:
#      - Extract: empID, deptCode, empLName, empName, empRateHr.
#      - Validate: empRateHr must be non-negative float.
#      - Check duplicate: SELECT 1 FROM Employees WHERE empID = ?
#      - Check foreign key: SELECT 1 FROM Departments WHERE depCode = ?
#      - Query: INSERT INTO Employees (empID, deptCode, empName, empLName, empRateHr) VALUES (?, ?, ?, ?, ?)
#      - Flash success and redirect to /employees.
# ============================================================================
@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    if not department_choices():
        flash("Add a department before adding an employee.", "error")
        return redirect(url_for("departments"))

    if request.method == "POST":
        try:
            emp_id = parse_int(request.form.get("empID"), "Employee ID")
            dept_code = parse_int(request.form.get("deptCode"), "Department")
            last_name = require_text(request.form.get("empLName"), "Last name")
            first_name = require_text(request.form.get("empName"), "First name")
            rate = parse_rate(request.form.get("empRateHr"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_employee_form()

        db = get_db()
        if db.execute("SELECT 1 FROM Employees WHERE empID = ?", (emp_id,)).fetchone():
            flash("That employee ID is already used.", "error")
            return render_employee_form()
        if not db.execute(
            "SELECT 1 FROM Departments WHERE depCode = ?",
            (dept_code,),
        ).fetchone():
            flash("Choose a valid department.", "error")
            return render_employee_form()

        db.execute(
            """
            INSERT INTO Employees (empID, deptCode, empName, empLName, empRateHr)
            VALUES (?, ?, ?, ?, ?)
            """,
            (emp_id, dept_code, first_name, last_name, rate),
        )
        db.commit()
        flash("Employee saved.", "success")
        return redirect(url_for("employees"))

    return render_employee_form()


# ============================================================================
# ### SKILLS TEST TASK 3.3: EDIT EMPLOYEE RECORD
# OBJECTIVE: Modify department, name, or hourly rate for an existing employee.
# WHAT NEEDS TO BE DONE:
#   1. Lookup employee by empID. If not found, flash error and redirect.
#   2. POST: Validate updated fields and deptCode validity.
#   3. Query:
#      UPDATE Employees SET deptCode = ?, empName = ?, empLName = ?, empRateHr = ? WHERE empID = ?
#   4. Commit changes, flash success, and redirect to /employees.
# ============================================================================
@app.route("/employees/<int:emp_id>/edit", methods=["GET", "POST"])
def edit_employee(emp_id):
    db = get_db()
    employee = db.execute(
        """
        SELECT empID, deptCode, empName, empLName, empRateHr
        FROM Employees
        WHERE empID = ?
        """,
        (emp_id,),
    ).fetchone()
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))

    if request.method == "POST":
        try:
            dept_code = parse_int(request.form.get("deptCode"), "Department")
            last_name = require_text(request.form.get("empLName"), "Last name")
            first_name = require_text(request.form.get("empName"), "First name")
            rate = parse_rate(request.form.get("empRateHr"))
        except ValueError as exc:
            flash(str(exc), "error")
            return render_employee_form(employee)

        if not db.execute(
            "SELECT 1 FROM Departments WHERE depCode = ?",
            (dept_code,),
        ).fetchone():
            flash("Choose a valid department.", "error")
            return render_employee_form(employee)

        db.execute(
            """
            UPDATE Employees
            SET deptCode = ?, empName = ?, empLName = ?, empRateHr = ?
            WHERE empID = ?
            """,
            (dept_code, first_name, last_name, rate, emp_id),
        )
        db.commit()
        flash("Employee updated.", "success")
        return redirect(url_for("employees"))

    return render_employee_form(employee)


# ============================================================================
# ### SKILLS TEST TASK 3.4: DELETE EMPLOYEE (ATTENDANCE AUDIT GUARD)
# OBJECTIVE: Prevent deleting an employee who has existing attendance logs.
# WHAT NEEDS TO BE DONE:
#   1. Check if employee has attendance records: SELECT 1 FROM Attendance WHERE empID = ?
#   2. If records exist, flash error and block deletion.
#   3. Otherwise: DELETE FROM Employees WHERE empID = ?
#   4. Commit transaction and redirect to /employees.
# ============================================================================
@app.route("/employees/<int:emp_id>/delete", methods=["POST"])
def delete_employee(emp_id):
    db = get_db()
    employee = db.execute(
        "SELECT empID FROM Employees WHERE empID = ?",
        (emp_id,),
    ).fetchone()
    if employee is None:
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))

    in_use = db.execute(
        "SELECT 1 FROM Attendance WHERE empID = ?",
        (emp_id,),
    ).fetchone()
    if in_use:
        flash("This employee has attendance records and cannot be deleted.", "error")
        return redirect(url_for("employees"))

    try:
        db.execute("DELETE FROM Employees WHERE empID = ?", (emp_id,))
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        flash("This employee has attendance records and cannot be deleted.", "error")
        return redirect(url_for("employees"))

    flash("Employee deleted.", "success")
    return redirect(url_for("employees"))


# ============================================================================
# ### SKILLS TEST TASK 4.1: LIST ALL ATTENDANCE LOGS
# OBJECTIVE: Retrieve all recorded time logs ordered by record number attRN.
# WHAT NEEDS TO BE DONE:
#   1. Query: SELECT attRN, empID, attDate, attTimeIn, attTimeOut, attStat FROM Attendance ORDER BY attRN
#   2. Render attendance.html passing the list of records.
# ============================================================================
@app.route("/attendance")
def attendance():
    rows = get_db().execute(
        """
        SELECT attRN, empID, attDate, attTimeIn, attTimeOut, attStat
        FROM Attendance
        ORDER BY attRN
        """
    ).fetchall()
    return render_template("attendance.html", records=rows)


def employee_choices():
    return get_db().execute(
        """
        SELECT empID, empName, empLName
        FROM Employees
        ORDER BY empID
        """
    ).fetchall()


# ============================================================================
# ### SKILLS TEST TASK 4.2: RECORD DAILY TIME RECORD (TIME IN / TIME OUT)
# OBJECTIVE: Validate employee selection, date, and clock times.
# Ensure Time Out is strictly after Time In.
# WHAT NEEDS TO BE DONE:
#   1. Verify employee list is not empty.
#   2. POST:
#      - Extract: empID, attDate (YYYY-MM-DD), attTimeIn (HH:MM), attTimeOut (HH:MM).
#      - Call build_attendance_times() to parse and ensure end > start.
#      - Validate that chosen empID exists.
#      - Query: INSERT INTO Attendance (empID, attDate, attTimeIn, attTimeOut, attStat) VALUES (?, ?, ?, ?, 'Not')
#      - Commit, flash "Attendance recorded.", and redirect to /attendance.
# ============================================================================
@app.route("/attendance/record", methods=["GET", "POST"])
def record_attendance():
    if not employee_choices():
        flash("Add an employee before recording attendance.", "error")
        return redirect(url_for("employees"))

    if request.method == "POST":
        try:
            emp_id = parse_int(request.form.get("empID"), "Employee")
            att_date, time_in, time_out = build_attendance_times(
                request.form.get("attDate"),
                request.form.get("attTimeIn"),
                request.form.get("attTimeOut"),
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("attendance_form.html", employees=employee_choices())

        db = get_db()
        if not db.execute("SELECT 1 FROM Employees WHERE empID = ?", (emp_id,)).fetchone():
            flash("Choose a valid employee.", "error")
            return render_template("attendance_form.html", employees=employee_choices())

        db.execute(
            """
            INSERT INTO Attendance (empID, attDate, attTimeIn, attTimeOut, attStat)
            VALUES (?, ?, ?, ?, ?)
            """,
            (emp_id, att_date, time_in, time_out, STATUS_NOT),
        )
        db.commit()
        flash("Attendance recorded.", "success")
        return redirect(url_for("attendance"))

    return render_template("attendance_form.html", employees=employee_choices())


# ============================================================================
# ### SKILLS TEST TASK 4.3: CANCEL ATTENDANCE RECORD (SOFT STATUS UPDATE)
# OBJECTIVE: Implement soft-status cancellation to preserve audit trails.
# WHAT NEEDS TO BE DONE:
#   1. Query: UPDATE Attendance SET attStat = 'Cancelled' WHERE attRN = ? AND attStat = 'Not'
#   2. Check rowcount:
#      - If changed > 0: flash "Attendance record cancelled."
#      - If changed == 0: inspect row to see if already cancelled or non-existent, flash appropriate error.
#   3. Commit and redirect to /attendance.
# ============================================================================
@app.route("/attendance/<int:att_rn>/cancel", methods=["POST"])
def cancel_attendance(att_rn):
    db = get_db()
    updated = db.execute(
        "UPDATE Attendance SET attStat = ? WHERE attRN = ? AND attStat = ?",
        (STATUS_CANCELLED, att_rn, STATUS_NOT),
    )
    changed = updated.rowcount
    db.commit()
    if changed:
        flash("Attendance record cancelled.", "success")
        return redirect(url_for("attendance"))

    existing = db.execute(
        "SELECT attStat FROM Attendance WHERE attRN = ?",
        (att_rn,),
    ).fetchone()
    if existing is None:
        flash("Attendance record not found.", "error")
    else:
        flash("That record is already cancelled.", "error")
    return redirect(url_for("attendance"))


@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")


def active_attendance(where_sql, params):
    rows = get_db().execute(
        f"""
        SELECT attRN, empID, attDate, attTimeIn, attTimeOut
        FROM Attendance
        WHERE attStat = ? AND {where_sql}
        ORDER BY attDate, attTimeIn, attRN
        """,
        (STATUS_NOT, *params),
    ).fetchall()
    return with_hours(rows)


# ============================================================================
# ### SKILLS TEST TASK 5.1: EMPLOYEE ATTENDANCE & PAYROLL MONITORING
# OBJECTIVE: Look up an employee, fetch valid attendance rows (attStat = 'Not'),
# calculate total hours worked, and compute gross salary:
#   Gross Salary = empRateHr * total_hours
# WHAT NEEDS TO BE DONE:
#   1. Extract ?empID query parameter.
#   2. Query employee details with department join.
#   3. Query active attendance rows and compute elapsed hours per shift.
#   4. Compute cumulative total hours and gross salary.
#   5. Render monitor_employee.html with report dictionary.
# ============================================================================
@app.route("/monitoring/employee")
def monitor_employee():
    report = None
    emp_raw = request.args.get("empID", "").strip()
    if emp_raw:
        try:
            emp_id = parse_int(emp_raw, "Employee number")
        except ValueError as exc:
            flash(str(exc), "error")
        else:
            employee = get_db().execute(
                """
                SELECT e.empID, e.empName, e.empLName, e.empRateHr, d.depName
                FROM Employees e
                JOIN Departments d ON d.depCode = e.deptCode
                WHERE e.empID = ?
                """,
                (emp_id,),
            ).fetchone()
            if employee is None:
                flash("Employee not found.", "error")
            else:
                records, total_hours = active_attendance("empID = ?", (emp_id,))
                report = {
                    "employee": employee,
                    "records": records,
                    "total_hours": total_hours,
                    "salary": round(employee["empRateHr"] * total_hours, 2),
                }
    return render_template(
        "monitor_employee.html",
        report=report,
        generated=today_text(),
    )


# ============================================================================
# ### SKILLS TEST TASK 5.2: DATE-RANGE ATTENDANCE AUDIT MONITORING
# OBJECTIVE: Filter active attendance records between two inclusive dates
# and compute total collective working hours.
# WHAT NEEDS TO BE DONE:
#   1. Extract ?date_from and ?date_to query parameters.
#   2. Validate dates: ensure start_date <= end_date.
#   3. Query:
#      SELECT attRN, empID, attDate, attTimeIn, attTimeOut FROM Attendance
#      WHERE attStat = 'Not' AND attDate >= ? AND attDate <= ?
#   4. Compute hours for each shift and sum total hours rendered.
#   5. Render monitor_range.html with report dictionary.
# ============================================================================
@app.route("/monitoring/range")
def monitor_range():
    report = None
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    if date_from or date_to:
        try:
            start = parse_date(date_from, "Date From")
            end = parse_date(date_to, "Date To")
            if start > end:
                raise ValueError("Date From must be on or before Date To.")
        except ValueError as exc:
            flash(str(exc), "error")
        else:
            records, total_hours = active_attendance(
                "attDate >= ? AND attDate <= ?",
                (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")),
            )
            report = {
                "records": records,
                "total_hours": total_hours,
                "date_from": format_day(start),
                "date_to": format_day(end),
            }
    return render_template(
        "monitor_range.html",
        report=report,
        generated=today_text(),
    )


init_db()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
