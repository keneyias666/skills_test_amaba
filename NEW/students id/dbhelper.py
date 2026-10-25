# ============================================================================
# SKILLS TEST QUESTIONNAIRE: STUDENT ID DATABASE HELPER (dbhelper.py)
# ============================================================================
# EXAM SCENARIO: Single-table SQLite database operations for student records.
#
# CANDIDATE TASKS & OBJECTIVES (WHAT NEEDS TO BE DONE):
# 1. DATABASE SCHEMA:
#    - Table: "students"
#    - Columns: id (INTEGER PK AUTOINCREMENT), student_id (TEXT UNIQUE),
#      name (TEXT), course (TEXT), score (REAL), date_added (TEXT).
# 2. CRUD FUNCTIONS TO IMPLEMENT/VERIFY:
#    - connect(): Establish active SQLite connection.
#    - create_table(): Execute table DDL with auto-increment and unique constraint.
#    - add_student(): Insert record with auto-timestamp (YYYY-MM-DD HH:MM:SS).
#    - get_all_students(): Return all rows ordered descending by id.
#    - search_student(): Multi-column case-insensitive search (student_id OR name).
#    - get_student(): Retrieve single record by id.
#    - update_student(): Update name, course, score by id.
#    - delete_student(): Delete record by id.
# ============================================================================

import sqlite3
from datetime import datetime

# SKILLS TEST: Change this to your exam's database filename
DB_NAME = "students.db"

def connect():
    """Create and return a database connection. No changes typically needed."""
    return sqlite3.connect(DB_NAME)

def create_table():
    """
    SKILLS TEST: Create the main table.
    Change table name, column names, and types to match your exam.
    - id = auto-increment primary key (hidden, used internally for edit/delete)
    - student_id = the visible student ID field (UNIQUE to prevent duplicates)
    - name, course = text fields
    - score = REAL (decimal/float for numeric scores)
    - date_added = filled manually via Python datetime in add_student()
    """
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Rename "students" and all columns below
    cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    name TEXT,
    course TEXT,
    score REAL,
    date_added TEXT
)
""")

    conn.commit()
    conn.close()


# SKILLS TEST: ADD / INSERT — Creates a new record
# student_id is the user-visible ID, not the auto-increment id.
# UNIQUE constraint on student_id prevents duplicate entries.
# date_added is set automatically via Python datetime.now().
# Change parameter names and SQL column names to match your exam.
# CREATE
def add_student(student_id, name, course, score):
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Auto-generate current date/time for date_added field
    # Format: "YYYY-MM-DD HH:MM:SS" — change format string if exam requires
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # SKILLS TEST: Change table name and column names
    cursor.execute("""
    INSERT INTO students (student_id, name, course, score, date_added)
    VALUES (?, ?, ?, ?, ?)
    """, (student_id, name, course, score, date_added))

    conn.commit()
    conn.close()


# SKILLS TEST: GET ALL — Fetches every record in the table
# Returns a list of tuples (not dicts) since no row_factory is set.
# Access by index: row[0]=id, row[1]=student_id, row[2]=name, etc.
# READ
def get_all_students():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()
    return data


# SKILLS TEST: SEARCH — Finds records matching a keyword
# Uses LIKE '%keyword%' for partial matching.
# Currently searches: student_id and name only.
# Add more OR conditions if exam needs to search additional columns.
# SEARCH
def search_student(keyword):
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Add/remove LIKE columns as needed for your exam
    # To search more columns: OR course LIKE ? OR score LIKE ?
    # (and add more like parameters to the tuple)
    cursor.execute("""
    SELECT * FROM students
    WHERE student_id LIKE ? OR name LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    data = cursor.fetchall()
    conn.close()
    return data


# SKILLS TEST: GET ONE — Fetches a single record by auto-increment id
# Used by the edit route: /edit/<id>
# Change table name and WHERE column if needed.
# GET ONE
def get_student(id):
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: WHERE uses the auto-increment "id", not "student_id"
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    data = cursor.fetchone()

    conn.close()
    return data


# SKILLS TEST: UPDATE — Modifies an existing record
# Updates by auto-increment id (not student_id).
# Note: student_id is NOT updated here (it's the immutable identifier).
# Change SET columns and WHERE clause for your exam.
# UPDATE
def update_student(id, name, course, score):
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Change "students", SET columns, and WHERE column
    cursor.execute("""
    UPDATE students
    SET name = ?, course = ?, score = ?
    WHERE id = ?
    """, (name, course, score, id))

    conn.commit()
    conn.close()


# SKILLS TEST: DELETE — Removes a record by auto-increment id (HARD delete)
# This permanently removes the record. For SOFT delete, use:
#   UPDATE students SET is_deleted = 1 WHERE id = ?
# Change table name and WHERE column for your exam.
# DELETE
def delete_student(id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()
