# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 03
## Event Registration & Fee Calculation System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-EVENT-03`
- **Course / Module:** Relational Database Normalization & Financial Transactions
- **Allowed Time:** 2.5 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
*Premier Events Group* coordinates conferences, seminars, and technical workshops. Attendees register for specific events with predetermined base registration fees (`evRFee`). Depending on attendee status (e.g. Early Bird, Student, Senior), a discount rate percentage (`partDRate`) is applied to compute the final payable fee (`regFPaid`).

The system requires an interconnected 3-tier database schema:
1. **Master Table (`Events`):** Details of the event, venue, date, and base fee.
2. **Participant Table (`Participants`):** Attendee biographical data and discount percentage.
3. **Transaction Table (`Registration`):** Financial ledger record linking participant to payment date, final amount paid, and payment method (`Card` or `Cash`).

As the examinee, **you must implement and verify the entire 3-table relational workflow**, multi-table JOIN reports, and discount computation.

---

## 2. System Architecture & Directory Layout

```text
NEW/SIMple/
├── reg.py          # Unified Flask application with 3-table CRUD routes
├── requirements.txt # Dependencies
├── sqlite3.exe     # Local SQLite CLI binary
├── database/
│   └── events_registration.db  # Relational SQLite database
└── templates/
    └── index.html  # Multi-section management dashboard
```

---

## 3. Database Specification & Data Dictionary

Database path: `database/events_registration.db`
Relational enforcement: `PRAGMA foreign_keys = ON;`

### Table 1: `Events` (Master Event Catalog)
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `evCode` | INTEGER | PRIMARY KEY AUTOINCREMENT | Event numeric code |
| `evName` | TEXT | NOT NULL | Title of event / conference |
| `evDate` | TEXT | NOT NULL | Scheduled date (`YYYY-MM-DD`) |
| `evVenue` | TEXT | NOT NULL | Venue location / hall |
| `evRFee` | REAL | NOT NULL | Base registration fee in PHP (₱) |

### Table 2: `Participants` (Attendee Registry)
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `partID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique participant ID |
| `evCode` | INTEGER | NOT NULL, FK | References `Events(evCode)` |
| `partfName` | TEXT | NOT NULL | First name |
| `partlName` | TEXT | NOT NULL | Last name |
| `partDRate` | REAL | NOT NULL, DEFAULT 0 | Discount rate percentage (e.g. `10.0` for 10%) |

### Table 3: `Registration` (Financial Transaction Log)
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `regCode` | INTEGER | PRIMARY KEY AUTOINCREMENT | Transaction receipt number |
| `partID` | INTEGER | NOT NULL, FK | References `Participants(partID)` |
| `regDate` | TEXT | NOT NULL | Date of payment (`YYYY-MM-DD`) |
| `regFPaid` | REAL | NOT NULL | Final net fee paid |
| `regPMode` | TEXT | NOT NULL, CHECK(`regPMode IN ('Card','Cash')`) | Payment mode |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Relational Database Setup (20 Points)
- [ ] **Task 1.1 — Foreign Key Enforcement:** Ensure the SQLite connection context manager executes `PRAGMA foreign_keys = ON;`.
- [ ] **Task 1.2 — 3-Tier Relational Schema:** Create `Events`, `Participants`, and `Registration` tables matching all foreign keys and the `CHECK(regPMode IN ('Card','Cash'))` constraint.

### Part 2: Event Catalog Management (20 Points)
- [ ] **Task 2.1 — Add Event:** Validate that `evName`, `evDate`, and `evVenue` are non-empty and `evRFee >= 0`. Insert into `Events`.
- [ ] **Task 2.2 — List Events:** Display all events in a summary grid.
- [ ] **Task 2.3 — Delete Event:** Delete an event only if no participants are registered for it (or handle cascade safely).

### Part 3: Participant Enrollment & Net Fee Math (30 Points)
- [ ] **Task 3.1 — Discount Math Calculation:**
  Retrieve the base event fee `evRFee`. Compute final fee:
  $$\text{regFPaid} = \text{evRFee} \times \left(1 - \frac{\text{partDRate}}{100}\right)$$
  Ensure `regFPaid` cannot be negative.
- [ ] **Task 3.2 — Atomic Dual-Table Insertion:**
  Within a single transaction, insert the attendee into `Participants` and immediately record the payment ledger into `Registration`.
- [ ] **Task 3.3 — Payment Mode Constraint:**
  Validate that `regPMode` is strictly `'Card'` or `'Cash'`. Reject invalid inputs with a flash alert.

### Part 4: Multi-Table Reporting & Summaries (20 Points)
- [ ] **Task 4.1 — 3-Table JOIN Query:**
  Build a query joining `Registration`, `Participants`, and `Events`:
  ```sql
  SELECT r.regCode, p.partfName, p.partlName, e.evName, e.evRFee, p.partDRate, r.regFPaid, r.regPMode, r.regDate
  FROM Registration r
  JOIN Participants p ON p.partID = r.partID
  JOIN Events e ON e.evCode = p.evCode
  ORDER BY r.regCode DESC;
  ```
- [ ] **Task 4.2 — Financial Aggregation:**
  Compute total collected revenue across all registrations and display at the foot of the report table.

### Part 5: UI & UX Polish (10 Points)
- [ ] **Task 5.1 — Navigation Tabs / Sections:**
  Organize forms cleanly: Event Creation, Registration Form, Ledger Report.
- [ ] **Task 5.2 — Flash Messaging:**
  Show clear feedback messages on successful registrations or invalid inputs.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Relational Database** | 3-table schema, foreign keys, CHECK constraints | 20 pts |
| **Event Catalog** | Event CRUD operations, non-negative fee validation | 20 pts |
| **Registration & Fee Math** | Accurate percentage discount calculation, atomic transactions | 30 pts |
| **Reporting & Multi-Table Joins** | 3-table SQL JOIN query, financial aggregation | 20 pts |
| **UI & Feedback** | Jinja template, flash alerts, currency display | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Launch the Application:**
   ```bash
   python reg.py
   ```
2. **Access the Web Interface:**
   `http://127.0.0.1:5000/`
3. **Verification Steps:**
   - **Create Event:** Name `"PyCon 2026"`, Date `"2026-11-15"`, Venue `"Hall A"`, Fee `₱2,000.00`.
   - **Register Participant:** Name `"John Doe"`, Event `"PyCon 2026"`, Discount `10%`, Mode `"Card"`.
   - **Fee Verification:** Verify that Net Fee is computed as `₱1,800.00` (`2000 - 10%`).
   - **Constraint Verification:** Try entering payment mode `"Cheque"`. Ensure database or form rejects it.
