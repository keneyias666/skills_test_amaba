# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 07
## University Intramural Sports Management System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-INTRA-07`
- **Course / Module:** Advanced Enterprise Web Development & RBAC Systems
- **Allowed Time:** 3.5 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
*University of Cebu Main Campus* organizes an annual Intramurals festival comprising hundreds of student athletes, multi-category competitions (Athletic, Cultural, and Academic), and extensive faculty involvement.

Managing registrations manually led to double-booked athletes, non-eligible players, and lack of real-time roster verification.

As the lead software engineering examinee, **you must build and verify a Role-Based Access Control (RBAC) web application** supporting five distinct user roles:
1. **System Administrator (`admin`):** Full system control, department management, registration oversight, and metrics.
2. **Tournament Manager (`tournament manager`):** Coordinates specific sporting/cultural events, sets maximum participant quotas, and verifies player rosters.
3. **Coach (`coach`):** Oversees college athletes, approves team participation, and monitors student entries.
4. **College Dean (`dean`):** Exercises institutional governance over college athletes and staff endorsements.
5. **Student / Athlete (`athlete`):** Creates personal athlete profiles, supplies academic information, and signs up for approved events.

---

## 2. System Architecture & Directory Layout

```text
NEW/INSTRAMURALS/
├── main.py             # Flask application, route controllers, session & RBAC guards
├── dbhelper.py         # DBHelper class managing SQLite tables and operations
├── intramurals.db      # SQLite database file
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Unified institutional theme & responsive tables
└── templates/
    ├── base.html             # Base layout with role-aware navigation bar
    ├── home.html             # Public welcome page with registration anchor
    ├── login.html            # Authentication form
    ├── register.html         # User account creation (admin, coach, TM, etc.)
    ├── dashboard.html        # Admin metrics & high-level overview
    ├── departments.html      # Department registry and creation
    ├── events.html           # Event creation, category, and capacity control
    ├── athletes.html         # Roster list of registered student athletes
    ├── athlete_profile.html  # Detailed student athlete profile view
    ├── users.html            # System-wide account registry (Admin only)
    ├── people.html           # Staff roster (Coaches, Deans, Managers)
    └── profile.html          # Staff profile management page
```

---

## 3. Database Specification & Data Dictionary

Your database file must be `intramurals.db`. Relational integrity (`PRAGMA foreign_keys = ON;`) is mandatory.

### Table 1: `Registration` (User Credentials & Roles)
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `userName` | TEXT | PRIMARY KEY | Unique account username / ID |
| `password` | TEXT | NOT NULL | Account password |
| `confirmPassword` | TEXT | NOT NULL | Password confirmation field |
| `role` | TEXT | NOT NULL, CHECK(`role IN ('admin','athlete','tournament manager','coach','dean')`) | System role |

### Table 2: `Department`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `deptID` | TEXT | PRIMARY KEY | College Department Code (e.g. "CCS", "COE") |
| `deptName` | TEXT | NOT NULL | College Name (e.g. "College of Computer Studies") |

### Table 3: `TournamentManager`, `Coach`, `Dean` (Staff Profiles)
*Each staff table follows the unified structure:*
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `userName` | TEXT | PRIMARY KEY, FK | References `Registration(userName)` |
| `fName` | TEXT | NOT NULL | Staff first name |
| `lName` | TEXT | NOT NULL | Staff last name |
| `mobile` | TEXT | NOT NULL | Contact telephone / mobile number |
| `deptID` | TEXT | NOT NULL, FK | References `Department(deptID)` |

### Table 4: `Event`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `eventID` | INTEGER | PRIMARY KEY AUTOINCREMENT | Event numeric identifier |
| `category` | TEXT | NOT NULL, CHECK(`category IN ('Athletic','Cultural','Academic')`) | Event Category |
| `eventName` | TEXT | NOT NULL | Title of event (e.g. "Basketball Men") |
| `noOfParticipant` | INTEGER | NOT NULL, CHECK(`noOfParticipant > 0`) | Maximum allowed athletes |
| `tournamentManager` | TEXT | NOT NULL, FK | References `TournamentManager(userName)` |

### Table 5: `AthletesProfile`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `idNum` | TEXT | PRIMARY KEY | Student ID Number |
| `eventID` | INTEGER | NOT NULL, FK | References `Event(eventID)` |
| `deptID` | TEXT | NOT NULL, FK | References `Department(deptID)` |
| `lastName` | TEXT | NOT NULL | Student surname |
| `firstName` | TEXT | NOT NULL | Student given name |
| `middleInit` | TEXT | NULLABLE | Middle initial |
| `course` | TEXT | NOT NULL | Academic degree program (e.g. "BSIT") |
| `year` | TEXT | NOT NULL | Year level (`1st Year` through `5th Year`) |
| `civilStatus` | TEXT | NOT NULL | Civil status (`Single`, `Married`, etc.) |
| `gender` | TEXT | NOT NULL | `Male` or `Female` |
| `birthdate` | TEXT | NOT NULL | Date of birth (`YYYY-MM-DD`) |
| `contactNo` | TEXT | NOT NULL | Phone contact |
| `address` | TEXT | NOT NULL | Residential address |
| `coachID` | TEXT | NOT NULL, FK | Assigned Coach username |
| `deanID` | TEXT | NOT NULL, FK | Assigned Dean username |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Relational Schema & Seeding (20 Points)
- [ ] **Task 1.1 — Foreign Keys & Constraints:** Execute schema scripts with foreign keys active. Ensure CHECK constraints for roles, categories, and participant quantities.
- [ ] **Task 1.2 — Built-in Admin Account:** Seed a default Administrator account (`ADMIN001` with password `Admin@123`) if not present.
- [ ] **Task 1.3 — Baseline Colleges:** Pre-populate core university colleges (e.g., CCS, COE, CBA, CAS).

### Part 2: Authentication & Role-Based Access Control (25 Points)
- [ ] **Task 2.1 — Registration Validation:** Ensure `userName` is unique and `password == confirmPassword`. Create user with valid role.
- [ ] **Task 2.2 — Session Login & Landing Dispatch:** On login (`/login`), verify credentials, set `session["userName"]` and `session["role"]`. Route user to their corresponding landing module (`dashboard`, `athlete_profile`, or `profile`).
- [ ] **Task 2.3 — RBAC Decorator (`@require_login(roles=[...])`):** Protect sensitive routes. If an unauthorized role attempts access, flash `"Your role cannot open that module."` and redirect.
- [ ] **Task 2.4 — Dynamic Navigation Menu:** Build an adaptive top menu in `base.html` that changes options depending on the active session role.

### Part 3: Event & Staff Management (25 Points)
- [ ] **Task 3.1 — Department Registry (`/departments`):** Allow Admin to add new college departments.
- [ ] **Task 3.2 — Event Creation (`/events`):** Tournament Managers or Admins can register events, specify category (`Athletic`, `Cultural`, `Academic`), and assign a registered Tournament Manager.
- [ ] **Task 3.3 — Staff Profile Management (`/profile`):** Coaches, Deans, and Tournament Managers must be able to view and update their profile and department affiliation.

### Part 4: Athlete Registration & Verification (20 Points)
- [ ] **Task 4.1 — Athlete Profiling (`/athlete_profile`):** Athletes or coaches can fill out the complete profile form.
- [ ] **Task 4.2 — Capacity Limit Guard:** When registering an athlete for an event, check the count of existing entries against `noOfParticipant`. Reject if the event roster is full.
- [ ] **Task 4.3 — Participant Directory (`/athletes`):** Display registered competitors with options to search/filter by event, department, or student name.

### Part 5: UI & Error Handling (10 Points)
- [ ] **Task 5.1 — Flash Feedback:** Provide contextual flash notices for login failures, duplicate records, capacity limits, and successful saves.
- [ ] **Task 5.2 — Safe Logout:** Implement `/logout` that clears the session and returns to `/home`.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Relational Database** | Complete 7-table schema, foreign keys, CHECK constraints, admin seed | 20 pts |
| **Authentication & RBAC** | Session management, password validation, route decorator, dynamic menu | 25 pts |
| **Events & Staff Modules** | Event capacity limits, tournament manager assignment, staff profile forms | 25 pts |
| **Athlete Roster Management** | Comprehensive athlete profile validation, roster full check, participant query | 20 pts |
| **User Interface & UX** | Flash feedback, clean responsive layout, secure logout, error recovery | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch Application:**
   ```bash
   python main.py
   ```
3. **Open Browser:**
   Navigate to `http://127.0.0.1:5000`
4. **Default Test Accounts:**
   - **Administrator:** Username `ADMIN001`, Password `Admin@123`
   - Or register a new account on the home page with any of the 5 roles.
