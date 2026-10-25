# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 01
## Student ID & Grading Records System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-STUDENT-01`
- **Course / Module:** Web Systems Development & Database Fundamentals
- **Allowed Time:** 2 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
The *Academic Affairs and Registrar Office* requires a clean, single-table record management application to register incoming student examinees, assign their unique institutional Student ID numbers, record examination scores, and track timestamp of entry.

As the examinee taking this practical skills test, **you must implement and verify the full CRUD (Create, Read, Update, Delete) workflow** with live keyword searching and duplicate ID rejection.

---

## 2. System Architecture & Directory Layout

```text
NEW/students id/
├── main.py         # Flask routing, request handling, form extraction
├── dbhelper.py     # SQLite3 database helper functions
├── students.db     # SQLite database file (auto-created on startup)
├── sqlite3.exe     # Optional local SQLite CLI utility
└── templates/
    ├── index.html  # Main single-page dashboard (Add form + List + Search)
    └── edit.html   # Update view for modifying an existing record
```

---

## 3. Database Specification & Data Dictionary

Database filename: `students.db`

### Table: `students`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal system primary key |
| `student_id` | TEXT | UNIQUE, NOT NULL | School Student ID (e.g. `2024-0012`) |
| `name` | TEXT | NOT NULL | Complete student name |
| `course` | TEXT | NOT NULL | Degree program (e.g. `BSIT`, `BSCS`) |
| `score` | REAL | NOT NULL | Exam / Evaluation score |
| `date_added` | TEXT | NOT NULL | Timestamp (`YYYY-MM-DD HH:MM:SS`) |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Database Operations in `dbhelper.py` (30 Points)
- [ ] **Task 1.1 — Schema Creation (`create_table()`):**
  Create the `students` table if it does not already exist. Ensure `id` is `INTEGER PRIMARY KEY AUTOINCREMENT` and `student_id` has a `UNIQUE` constraint.
- [ ] **Task 1.2 — Add Record with Auto-Timestamp (`add_student()`):**
  Insert a new student with current timestamp generated via Python `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`.
- [ ] **Task 1.3 — Fetch All (`get_all_students()`):**
  Return all student rows ordered descending by `id`.
- [ ] **Task 1.4 — Search Query (`search_student(keyword)`):**
  Execute a `LIKE ?` search matching either `student_id` or `name` (case-insensitive substring match).
- [ ] **Task 1.5 — Get Single Record (`get_student(id)`):**
  Retrieve a specific student row by its numeric `id`.
- [ ] **Task 1.6 — Update Record (`update_student()`):**
  Update `name`, `course`, and `score` for the given `id`. Note: `student_id` is immutable.
- [ ] **Task 1.7 — Delete Record (`delete_student(id)`):**
  Execute `DELETE FROM students WHERE id = ?`.

### Part 2: Flask Routing & Controller Logic in `main.py` (40 Points)
- [ ] **Task 2.1 — Initialization:** Call `dbhelper.create_table()` on server launch.
- [ ] **Task 2.2 — Home Route (`/`):**
  - **POST:** Extract `student_id`, `name`, `course`, `score` from `request.form`. Call `dbhelper.add_student()`. Gracefully catch `sqlite3.IntegrityError` if a duplicate `student_id` is submitted. Redirect to `/`.
  - **GET:** Check for URL query parameter `?search=keyword`. If present, render search results; otherwise render all students.
- [ ] **Task 2.3 — Edit Route (`/edit/<int:id>`):**
  - **GET:** Fetch the student by `id` and render `edit.html` with form pre-populated.
  - **POST:** Update fields and redirect back to `/`.
- [ ] **Task 2.4 — Delete Route (`/delete/<int:id>`):**
  Delete the student record and redirect back to `/`.

### Part 3: UI & Templates (20 Points)
- [ ] **Task 3.1 — Add Form:** Inputs for `student_id`, `name`, `course`, `score` with submit button.
- [ ] **Task 3.2 — Search Bar:** Form submitting via GET `?search=...` with clear/reset option.
- [ ] **Task 3.3 — Records Table:** Render all student rows with Edit and Delete action links.
- [ ] **Task 3.4 — Empty State:** Display "No students found" if the database is empty.

### Part 4: Code Quality & Error Handling (10 Points)
- [ ] **Task 4.1:** Clean database connection closing (`conn.close()`) in every function.
- [ ] **Task 4.2:** Parameterized queries (`?`) to prevent SQL Injection.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Database Operations** | Schema setup, CRUD queries, auto-timestamp, search query | 30 pts |
| **Flask Routes & Controller** | GET/POST routing, form handling, duplicate prevention, redirects | 40 pts |
| **Frontend Templates** | Jinja rendering, pre-populated edit form, tables & search bar | 20 pts |
| **Security & Quality** | Parameterized queries, connection cleanup, error handling | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Run the Flask Server:**
   ```bash
   python main.py
   ```
2. **Access in Browser:**
   `http://127.0.0.1:5000/`
3. **Test Cases:**
   - **Insert:** Add student `2024-001`, `Alice Smith`, `BSIT`, `95.5`.
   - **Duplicate Test:** Attempt adding `2024-001` again. Ensure the system does not crash.
   - **Search:** Search `Alice` or `2024-001`.
   - **Edit:** Change Alice's score to `98.0`. Verify the update persists.
   - **Delete:** Delete the record. Verify the table is empty.
