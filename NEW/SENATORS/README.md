# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 04
## National Senatorial & Campus Voting System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-ELECT-04`
- **Course / Module:** Secure Web Applications, Relational Integrity & Tabulation Systems
- **Allowed Time:** 3 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
The *University Electoral Board* (or National Election Commission) requires an automated, tamper-resistant digital voting application for campus elections. Positions to be contested have distinct maximum seat capacities (e.g., 1 President, 1 Vice President, 12 Senators).

Voters must authenticate with their unique Voter ID and Password. Crucially:
1. Voters may cast their ballot only **once**; the system must mark their status as `hasVoted = 1` immediately upon submission.
2. For each contested position, the voter cannot select more candidates than the position's seat quota (`posSeats`). Over-voting must invalidate or reject the ballot with clear error notifications.
3. Soft-delete functionality (`status = 'inactive'`) must be used for candidates and positions so historical vote logs are never corrupted.
4. Live results must display vote counts and percentage share of total votes, and the Winners module must compute the top $N$ candidates per position based on seat limit.

As the examinee, **you must implement and verify the entire election management and ballot casting lifecycle**.

---

## 2. System Architecture & Directory Layout

```text
NEW/SENATORS/
├── main.py             # Flask application, route controllers, session & ballot checks
├── dbhelper.py         # Database access layer for positions, candidates, voters, votes
├── schema.sql          # SQL schema script defining tables, foreign keys, and indexes
├── Election.db         # SQLite database file
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Clean electoral theme
└── templates/
    ├── base.html            # Navigation and flash messages
    ├── index.html           # Home portal
    ├── login.html           # Voter sign-in
    ├── positions.html       # Position list
    ├── position_form.html   # Add/Edit position
    ├── candidates.html      # Candidate roster
    ├── candidate_form.html  # Add/Edit candidate
    ├── voters.html          # Voter registration registry
    ├── voter_form.html      # Register new voter
    ├── vote.html            # Official digital ballot
    ├── results.html         # Live tally and vote percentages
    └── winners.html         # Proclaimed top-N winners
```

---

## 3. Database Specification & Data Dictionary

Database path: `Election.db`
Relational enforcement: `PRAGMA foreign_keys = ON;`

### Table 1: `Positions`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `posID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Position ID |
| `posName` | TEXT | NOT NULL | Title (e.g. "Senator", "President") |
| `posSeats` | INTEGER | NOT NULL, CHECK(`posSeats >= 1`) | Maximum winners allowed |
| `posStatus` | TEXT | NOT NULL, DEFAULT `'active'` | `'active'` or `'inactive'` |

### Table 2: `Candidates`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `candID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Candidate ID |
| `posID` | INTEGER | NOT NULL, FK | References `Positions(posID)` |
| `candFName` | TEXT | NOT NULL | First name |
| `candMName` | TEXT | NULLABLE | Middle name |
| `candLName` | TEXT | NOT NULL | Last name |
| `candParty` | TEXT | NOT NULL | Political party / slate |
| `candStatus` | TEXT | NOT NULL, DEFAULT `'active'` | `'active'` or `'inactive'` |

### Table 3: `Voters`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `voterID` | TEXT | PRIMARY KEY | Unique Voter ID Number |
| `voterPass` | TEXT | NOT NULL | Password |
| `voterFName` | TEXT | NOT NULL | First name |
| `voterLName` | TEXT | NOT NULL | Last name |
| `hasVoted` | INTEGER | NOT NULL, DEFAULT 0 | `0` = Not voted, `1` = Has voted |
| `voterStatus`| TEXT | NOT NULL, DEFAULT `'active'` | `'active'` or `'inactive'` |

### Table 4: `Votes` (Ballot Ledger)
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `voteID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Vote receipt ID |
| `voterID` | TEXT | NOT NULL, FK | References `Voters(voterID)` |
| `candID` | INTEGER | NOT NULL, FK | References `Candidates(candID)` |
| `posID` | INTEGER | NOT NULL, FK | References `Positions(posID)` |
| `voteTime` | TEXT | NOT NULL | Timestamp of vote |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Schema Setup & Database Operations in `dbhelper.py` (25 Points)
- [ ] **Task 1.1 — Schema Execution:** Execute `schema.sql` at app startup to ensure all tables, constraints, and indexes exist.
- [ ] **Task 1.2 — Position & Candidate Management:**
  - `add_position(name, seats)`, `update_position()`, `deactivate_position()`.
  - `add_candidate(pos_id, first, middle, last, party)`, `deactivate_candidate()`.
- [ ] **Task 1.3 — Voter Authentication:**
  `authenticate_voter(voter_id, password)`: Return voter record if valid and `voterStatus == 'active'`; otherwise `None`.
- [ ] **Task 1.4 — Soft Delete Operations:**
  When deleting a position, candidate, or voter, update `status = 'inactive'`. Never hard-delete active election records.

### Part 2: Ballot Submission & Over-Voting Protection in `main.py` (35 Points)
- [ ] **Task 2.1 — Authentication & Session:**
  Implement `/login`. On success, store `session["voterID"]`. On `/logout`, clear session.
- [ ] **Task 2.2 — Pre-Voting Verification:**
  On `/vote`, verify voter is logged in and `hasVoted == 0`. If `hasVoted == 1`, redirect to `/results` with a flash message: `"You have already cast your vote."`
- [ ] **Task 2.3 — Seat Limit Enforcement:**
  For each contested position, extract chosen candidates:
  ```python
  selected_candidates = request.form.getlist(f"position_{pos['posID']}")
  if len(selected_candidates) > pos['posSeats']:
      flash(f"You can only select up to {pos['posSeats']} candidate(s) for {pos['posName']}.", "error")
      return redirect(url_for("vote"))
  ```
- [ ] **Task 2.4 — Atomic Ballot Recording:**
  In a single database transaction:
  1. Insert individual votes into `Votes` for every selected candidate.
  2. Update `Voters SET hasVoted = 1 WHERE voterID = ?`.
  3. Commit transaction and flash success message.

### Part 3: Live Results & Winner Determination (25 Points)
- [ ] **Task 3.1 — Tally Calculation (`/results`):**
  Group votes by candidate, count total votes, and calculate percentage share:
  $$\text{Percentage} = \left(\frac{\text{Candidate Votes}}{\text{Total Position Votes}}\right) \times 100\%$$
- [ ] **Task 3.2 — Winners Ranking (`/winners`):**
  For each position, sort candidates descending by vote count. Proclaim the top $N$ candidates where $N = \text{posSeats}$.

### Part 4: UI & Templates (15 Points)
- [ ] **Task 4.1 — Digital Ballot UI (`vote.html`):**
  Group candidates by position with clear indications of maximum allowable choices (e.g. *"Select up to 12 candidates"*).
- [ ] **Task 4.2 — Visual Progress & Percentages:**
  Display results with progress bars or formatted percentages (`##.##%`).

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Database & Schema Integrity** | 4-table schema, foreign keys, soft-delete, indexes | 25 pts |
| **Ballot Validation & Integrity** | Seat limit check, anti-duplicate voting, atomic commit | 35 pts |
| **Tabulation & Winners** | Live tally, correct percentage math, top-N winner slice | 25 pts |
| **UI Presentation & Security** | Ballot UX, session security, flash messaging | 15 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Flask Server:**
   ```bash
   python main.py
   ```
3. **Open Browser:**
   `http://127.0.0.1:5000/`
4. **Sample Test Flow:**
   - Register Positions: *President (1 seat)*, *Senators (12 seats)*.
   - Register Candidates under President and Senators.
   - Register a Voter (e.g., ID `VOTER-101`, Password `pass123`).
   - Log in as `VOTER-101` and navigate to `/vote`.
   - Try selecting 2 Presidents (Seat limit = 1). Verify system blocks over-voting.
   - Vote properly and submit. Check `/results` to confirm tally incremented.
   - Try voting again as `VOTER-101`. Verify system refuses access.
