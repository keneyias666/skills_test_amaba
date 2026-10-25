# PRACTICAL SKILLS TEST EXAMINATION PORTAL
## Full-Stack Web Development & Relational Database Systems

---

### REPOSITORY OVERVIEW
Welcome to the **Skills Test Practical Examination Suite**. This repository contains seven (7) standardized, standalone web application systems designed as practical test questionnaires for technical skill assessments, academic examinations, and coding certifications in Python, Flask, SQLite3, Jinja2, and Web Systems Engineering.

Each system in the [`NEW/`](./NEW/) directory represents an official practical examination scenario with an accompanying **Questionnaire Specification (`README.md`)** detailing:
- Scenario and business background
- Relational database schema and constraints
- Specific tasks and candidate requirements (**"What Needs To Be Done"**)
- 100-point standardized grading rubric
- Execution, testing, and verification procedures

---

## 1. Examination Systems Matrix

| # | System Title | Directory | Exam Code | Domain / Pattern | Duration | Points | Level |
|:---:|---|---|---|---|:---:|:---:|:---:|
| **01** | [Student ID & Grading Records](./NEW/students%20id/README.md) | `NEW/students id` | `SKILL-TEST-2026-STUDENT-01` | Single-table CRUD, search, unique constraints, timestamps | 2.0 hrs | 100 pts | Beginner |
| **02** | [Bookstore Inventory & Valuation](./NEW/Bookssyste,/README.md) | `NEW/Bookssyste,` | `SKILL-TEST-2026-BOOK-02` | Single-page action dispatch, inventory math, seed loader | 2.0 hrs | 100 pts | Intermediate |
| **03** | [Event Registration & Fee Math](./NEW/SIMple/README.md) | `NEW/SIMple` | `SKILL-TEST-2026-EVENT-03` | 3-table normalized schema, discount calculations, payment checks | 2.5 hrs | 100 pts | Intermediate |
| **04** | [Senatorial & Campus Voting](./NEW/SENATORS/README.md) | `NEW/SENATORS` | `SKILL-TEST-2026-ELECT-04` | Ballot seat quotas, anti-double voting, soft deletes, live tallies | 3.0 hrs | 100 pts | Advanced |
| **05** | [Veterinary Clinic & Consultations](./NEW/my%20pt/README.md) | `NEW/my pt` | `SKILL-TEST-2026-PET-05` | Healthcare records, 12h/24h time parse, multi-criteria inquiry | 3.0 hrs | 100 pts | Advanced |
| **06** | [Attendance & Payroll Monitoring](./NEW/Attendace%20monitoring%20system/README.md) | `NEW/Attendace monitoring system` | `SKILL-TEST-2026-ATT-06` | DTR logging, hours worked calculation, hourly rates, payroll audit | 3.0 hrs | 100 pts | Advanced |
| **07** | [University Intramural Sports](./NEW/INSTRAMURALS/README.md) | `NEW/INSTRAMURALS` | `SKILL-TEST-2026-INTRA-07` | 5-role RBAC, event quota management, roster verification | 3.5 hrs | 100 pts | Advanced |

---

## 2. In-Code "What Needs To Be Done" Structure

Across all codebases in this repository, every module, helper function, database query, and route controller is thoroughly annotated with standardized exam guide comments:

```python
# ============================================================================
# ### SKILLS TEST TASK [X.X]: <TASK TITLE>
# OBJECTIVE:
#   <Summary of technical objective>
# WHAT NEEDS TO BE DONE:
#   1. <Step-by-step instruction for candidate>
#   2. <Validation and parameter requirements>
#   3. <Expected SQL query / return value / error handling>
# ============================================================================
```

Candidates can navigate directly into any system's source code to view exact tasks, parameter signatures, and implementation requirements.

---

## 3. General Instructions for Candidates

1. **Environment Setup:**
   Ensure you have Python 3.10+ installed. It is recommended to create a dedicated virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. **Install Common Dependencies:**
   Each project includes a `requirements.txt` file (or relies on core `Flask` and `sqlite3`):
   ```bash
   pip install flask
   ```
3. **Database Integrity & Foreign Keys:**
   - Always verify that `PRAGMA foreign_keys = ON;` is executed on every SQLite connection.
   - Use parameterized queries (`?`) for all SQL operations to prevent SQL Injection vulnerabilities.
   - Maintain referential integrity; prevent orphaned records when updating or deleting.
4. **Logical (Soft) Deletion Standards:**
   - In Systems 04, 05, and 06, records must **never** be hard-deleted from the database. Use status flags (`is_deleted = 1` or `attStat = 'Cancelled'` or `status = 'inactive'`) to preserve audit trails.
5. **Form Validation & User Feedback:**
   - Always sanitize and validate form inputs.
   - Display informative Flask flash messages (`flash("...", "success" | "error")`) on both successful operations and validation errors.

---

## 4. Standard Evaluation Rubric (100 Points Total)

Each skills test questionnaire is evaluated according to the following universal criteria:

| Evaluation Dimension | Description | Points |
|---|---|:---:|
| **Database Engineering** | Schema correctness, primary/foreign keys, CHECK constraints, auto-increment, data types, connection cleanup | 20 – 30 pts |
| **Application & Routing Logic** | RESTful route handling, GET/POST parameter extraction, session security, redirects | 25 – 40 pts |
| **Data Validation & Business Logic** | Edge case checks, duplicate prevention, mathematical formulas (discounts, hours, seats), soft deletion | 20 – 25 pts |
| **UI Presentation & Templates** | Jinja2 syntax, form control population, table formatting, responsive layouts, flash alerts | 10 – 20 pts |
| **Code Hygiene & Security** | Parameterized queries, error recovery, modular architecture, code documentation | 10 pts |
| **TOTAL SCORE** | **Standard Practical Skills Test Score** | **100 pts** |

---

## 5. Submission & Git Repository

All changes, questionnaires, and commented codebases are published to the official GitHub repository:
- **Repository URL:** [https://github.com/keneyias666/skills_test_amaba](https://github.com/keneyias666/skills_test_amaba)
- **Primary Branch:** `main`
