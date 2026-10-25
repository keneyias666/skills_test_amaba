"""
============================================================================
SKILLS TEST QUESTIONNAIRE: EVENT REGISTRATION & FINANCIAL SYSTEM (reg.py)
============================================================================
EXAM SCENARIO:
  A conference organization registers participants across various events.
  Registration fee varies by event, and participants may have a discount rate.
  Payment mode is constrained to 'Card' or 'Cash'.

CANDIDATE TASKS & OBJECTIVES (WHAT NEEDS TO BE DONE):
1. RELATIONAL DATABASE SETUP (init_db):
   - Table 1 (Events): evCode (PK), evName, evDate, evVenue, evRFee.
   - Table 2 (Participants): partID (PK), evCode (FK), partfName, partlName, partDRate.
   - Table 3 (Registration): regCode (PK), partID (FK), regDate, regFPaid,
     regPMode CHECK IN ('Card', 'Cash').
   - Enable PRAGMA foreign_keys = ON;
2. ROUTING & CONTROLLERS:
   - Event creation, listing, updating, and safe deletion.
   - Participant registration with discount calculation:
     regFPaid = evRFee * (1 - partDRate / 100)
   - Atomic recording of Participant and Registration ledger row.
3. FINANCIAL REPORTING:
   - 3-table JOIN query displaying all transaction ledgers and revenue sum.
============================================================================
"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
# SKILLS TEST: Change this secret key if the exam requires a specific one
app.secret_key = "dev"

_BASE = os.path.dirname(os.path.abspath(__file__))
# SKILLS TEST: Change the database filename below to match your exam requirements
# e.g., "school_registration.db", "hotel_booking.db", etc.
DB = os.path.join(_BASE, "database", "events_registration.db")


def init_db():
    """
    SKILLS TEST — DATABASE SCHEMA SETUP
    This creates all tables. To adapt for a different exam scenario:
    1. Rename table names (Events → your_table_name)
    2. Rename columns (evCode → your_pk_name, evName → your_field, etc.)
    3. Add/remove columns as the exam requires
    4. Adjust data types: TEXT, INTEGER, REAL, etc.
    5. Adjust CHECK constraints (e.g., regPMode IN ('Card','Cash') → your values)
    6. Adjust FOREIGN KEY references between tables
    7. Add DEFAULT values if the exam requires them
    """
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            -- SKILLS TEST: TABLE 1 — Parent/Master table
            -- Change "Events" to your table name, rename all columns below
            -- evCode = auto-increment primary key
            -- evName = text field (e.g., event name, product name, course name)
            -- evDate = date field stored as TEXT in YYYY-MM-DD format
            -- evVenue = text field (e.g., location, address, room)
            -- evRFee = numeric/money field stored as REAL (e.g., price, fee, rate)
            CREATE TABLE IF NOT EXISTS Events (
                evCode INTEGER PRIMARY KEY AUTOINCREMENT,
                evName TEXT NOT NULL, evDate TEXT NOT NULL,
                evVenue TEXT NOT NULL, evRFee REAL NOT NULL);

            -- SKILLS TEST: TABLE 2 — Child table (belongs to Table 1)
            -- Change "Participants" to your table name
            -- partID = auto-increment primary key
            -- evCode = foreign key linking to Events table
            -- partfName, partlName = first/last name text fields
            -- partDRate = discount rate (numeric), default 0
            CREATE TABLE IF NOT EXISTS Participants (
                partID INTEGER PRIMARY KEY AUTOINCREMENT,
                evCode INTEGER NOT NULL, partfName TEXT NOT NULL,
                partlName TEXT NOT NULL, partDRate REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (evCode) REFERENCES Events(evCode));

            -- SKILLS TEST: TABLE 3 — Transaction table (belongs to Table 2)
            -- Change "Registration" to your table name
            -- regCode = auto-increment primary key
            -- partID = foreign key linking to Participants table
            -- regDate = transaction date
            -- regFPaid = computed fee (base fee - discount)
            -- regPMode = constrained text field: only 'Card' or 'Cash' allowed
            --   SKILLS TEST: Change these CHECK values to match exam requirements
            --   e.g., CHECK(status IN ('Pending','Approved','Rejected'))
            CREATE TABLE IF NOT EXISTS Registration (
                regCode INTEGER PRIMARY KEY AUTOINCREMENT,
                partID INTEGER NOT NULL, regDate TEXT NOT NULL,
                regFPaid REAL NOT NULL,
                regPMode TEXT NOT NULL CHECK(regPMode IN ('Card','Cash')),
                FOREIGN KEY (partID) REFERENCES Participants(partID));
            """
        )
        conn.commit()
    finally:
        conn.close()


@contextmanager
def db():
    """
    SKILLS TEST: Database connection context manager.
    You generally don't need to change this. It:
    - Opens a connection, enables foreign keys
    - Auto-commits on success, auto-rollbacks on error
    - Always closes the connection
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# SKILLS TEST: VALIDATION HELPERS
# These are reusable validators. Change the error messages to match your exam.
# You can copy these patterns for new field types (e.g., email, phone).

def num(x, label="Number"):
    """Validate and convert a numeric field. Change 'label' for custom error messages."""
    if not str(x or "").strip():
        raise ValueError(f"{label} required")
    try:
        return float(Decimal(str(x).strip()))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{label} invalid")


def dt(x, label="Date"):
    """Validate a date string in YYYY-MM-DD format."""
    if not str(x or "").strip():
        raise ValueError(f"{label} required")
    s = str(x).strip()
    try:
        date.fromisoformat(s)
    except ValueError:
        raise ValueError(f"{label} use YYYY-MM-DD")
    return s


def pid(x):
    """Validate an integer ID field."""
    if not str(x or "").strip():
        raise ValueError("ID required")
    try:
        return int(str(x).strip())
    except ValueError:
        raise ValueError("ID must be a number") from None


def pm(x):
    """
    SKILLS TEST: Validate a constrained choice field.
    Change ('Card', 'Cash') to match your exam's allowed values.
    e.g., ('Online', 'Walk-in'), ('Male', 'Female'), ('Active', 'Inactive')
    """
    m = (x or "").strip()
    if m not in ("Card", "Cash"):
        raise ValueError('Pay mode: Card or Cash')
    return m


_db_ok = False


@app.before_request
def _db_once():
    """Auto-initializes DB on first request. No changes needed."""
    global _db_ok
    if not _db_ok:
        init_db()
        _db_ok = True


# ============================================================================
# SKILLS TEST: HOME ROUTE — Lists all records + report/filter
# This is the main page. It loads Events, Participants, and Registrations.
# If you need separate pages per table, split this into multiple routes.
# ============================================================================
@app.route("/", methods=["GET"])
def home():
    ev_filter = request.args.get("ev")
    edit_ev = request.args.get("edit_ev", type=int)
    edit_p = request.args.get("edit_p", type=int)
    event_edit = None
    part_edit = None

    try:
        with db() as c:
            # SKILLS TEST: Change table/column names in all SELECT queries below
            events = c.execute("SELECT * FROM Events ORDER BY evCode").fetchall()
            participants = c.execute(
                """SELECT p.*, e.evName FROM Participants p
                   JOIN Events e ON p.evCode=e.evCode ORDER BY p.partID"""
            ).fetchall()
            # SKILLS TEST: This JOIN query pulls data from all 3 tables for display
            # Change table names, column names, and JOIN conditions to match your schema
            registrations = c.execute(
                """SELECT r.*, p.partfName, p.partlName, e.evName
                   FROM Registration r
                   JOIN Participants p ON r.partID=p.partID
                   JOIN Events e ON p.evCode=e.evCode
                   ORDER BY r.regDate DESC, r.regCode DESC"""
            ).fetchall()
            if edit_ev:
                event_edit = c.execute(
                    "SELECT * FROM Events WHERE evCode=?", (edit_ev,)
                ).fetchone()
            if edit_p:
                part_edit = c.execute(
                    "SELECT * FROM Participants WHERE partID=?", (edit_p,)
                ).fetchone()

            # SKILLS TEST: REPORT / FILTER SECTION
            # This section generates a filtered report by event code.
            # Change the filter field if exam requires filtering by something else
            # (e.g., by date range, by name, by status).
            report_ev = None
            report_rows = []
            agg = None
            if ev_filter and str(ev_filter).strip():
                try:
                    ec = int(str(ev_filter).strip())
                except ValueError:
                    flash("Bad event code", "danger")
                    ec = None
                if ec is not None:
                    report_ev = c.execute(
                        "SELECT * FROM Events WHERE evCode=?", (ec,)
                    ).fetchone()
                    if report_ev:
                        # SKILLS TEST: This builds the report detail rows
                        # TRIM(p.partfName||' '||p.partlName) concatenates first+last name
                        report_rows = c.execute(
                            """SELECT r.regDate, r.regFPaid,
                               TRIM(p.partfName||' '||p.partlName) AS fullName
                               FROM Registration r JOIN Participants p ON r.partID=p.partID
                               WHERE p.evCode=? ORDER BY r.regDate DESC""",
                            (ec,),
                        ).fetchall()
                        bf = float(report_ev["evRFee"])
                        # SKILLS TEST: AGGREGATION — COUNT and SUM for the report
                        # "n" = total registrations, "s" = total fees paid
                        # "disc" = total discount = (count * base_fee) - sum_paid
                        ar = c.execute(
                            """SELECT COUNT(*) AS n, COALESCE(SUM(r.regFPaid),0) AS s
                               FROM Registration r JOIN Participants p ON r.partID=p.partID
                               WHERE p.evCode=?""",
                            (ec,),
                        ).fetchone()
                        n, s = int(ar["n"]), float(ar["s"])
                        agg = {"n": n, "sum": s, "disc": n * bf - s, "base": bf}
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
        events, participants, registrations = [], [], []
        event_edit, part_edit = None, None
        report_ev, report_rows, agg = None, [], None

    # SKILLS TEST: Change template name if exam requires a different filename
    return render_template(
        "index.html",
        events=events,
        participants=participants,
        registrations=registrations,
        event_edit=event_edit,
        part_edit=part_edit,
        report_ev=report_ev,
        report_rows=report_rows,
        agg=agg,
        ev_filter=ev_filter or "",
    )


# ============================================================================
# SKILLS TEST: SAVE EVENT (INSERT + UPDATE)
# This handles both adding new events and updating existing ones.
# Pattern: If form has a hidden "evCode" field → UPDATE, else → INSERT
# COPY THIS PATTERN for any new table you need to add.
# ============================================================================
@app.post("/save_event")
def save_event():
    try:
        # SKILLS TEST: Change form field names to match your HTML form
        code = request.form.get("evCode")
        name = (request.form.get("evName") or "").strip()
        venue = (request.form.get("evVenue") or "").strip()
        d = dt(request.form.get("evDate"), "Date")
        fee = num(request.form.get("evRFee"), "Fee")
        # SKILLS TEST: Add/change validation rules as needed
        if not name or not venue:
            raise ValueError("Name and venue required")
        if fee < 0:
            raise ValueError("Fee can't be negative")
        with db() as c:
            if code:
                # SKILLS TEST: UPDATE — change column names and table name
                c.execute(
                    "UPDATE Events SET evName=?,evDate=?,evVenue=?,evRFee=? WHERE evCode=?",
                    (name, d, venue, fee, int(code)),
                )
                flash("Event updated", "success")
            else:
                # SKILLS TEST: INSERT — change column names and table name
                c.execute(
                    "INSERT INTO Events (evName,evDate,evVenue,evRFee) VALUES (?,?,?,?)",
                    (name, d, venue, fee),
                )
                flash("Event added", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
    return redirect(url_for("home"))


# SKILLS TEST: DELETE EVENT
# Uses foreign key protection — can't delete if child records exist.
# Change table name and primary key column to match your schema.
@app.post("/delete_event/<int:ev_code>")
def delete_event(ev_code):
    try:
        with db() as c:
            c.execute("DELETE FROM Events WHERE evCode=?", (ev_code,))
    except sqlite3.IntegrityError:
        flash("Can't delete: still used by participants", "danger")
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
    else:
        flash("Event deleted", "success")
    return redirect(url_for("home"))


# ============================================================================
# SKILLS TEST: SAVE PARTICIPANT (INSERT + UPDATE)
# Same INSERT/UPDATE pattern as save_event.
# Validates that the foreign key (evCode) exists in the Events table.
# SKILLS TEST: Change field names, table name, and foreign key checks.
# ============================================================================
@app.post("/save_participant")
def save_participant():
    try:
        pcode = request.form.get("partID")
        ec = pid(request.form.get("evCode"))
        fn = (request.form.get("partfName") or "").strip()
        ln = (request.form.get("partlName") or "").strip()
        dr = num(request.form.get("partDRate"), "Discount")
        if not fn or not ln:
            raise ValueError("Names required")
        if dr < 0:
            raise ValueError("Discount can't be negative")
        with db() as c:
            # SKILLS TEST: Foreign key validation — checks parent record exists
            if not c.execute("SELECT 1 FROM Events WHERE evCode=?", (ec,)).fetchone():
                raise ValueError("Bad event code")
            if pcode:
                c.execute(
                    "UPDATE Participants SET evCode=?,partfName=?,partlName=?,partDRate=? WHERE partID=?",
                    (ec, fn, ln, dr, int(pcode)),
                )
                flash("Participant updated", "success")
            else:
                c.execute(
                    "INSERT INTO Participants (evCode,partfName,partlName,partDRate) VALUES (?,?,?,?)",
                    (ec, fn, ln, dr),
                )
                flash("Participant added", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
    return redirect(url_for("home"))


# SKILLS TEST: DELETE PARTICIPANT — same pattern as delete_event
@app.post("/delete_participant/<int:part_id>")
def delete_participant(part_id):
    try:
        with db() as c:
            c.execute("DELETE FROM Participants WHERE partID=?", (part_id,))
    except sqlite3.IntegrityError:
        flash("Can't delete: has registrations", "danger")
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
    else:
        flash("Participant deleted", "success")
    return redirect(url_for("home"))


# ============================================================================
# SKILLS TEST: REGISTER (Transaction/INSERT with computed field)
# This is the KEY BUSINESS LOGIC:
#   paid = base_fee (from Events) - discount_rate (from Participants)
# SKILLS TEST: Change the formula if exam requires different computation.
# e.g., total = quantity * price, net = gross - tax, etc.
# ============================================================================
@app.post("/register")
def register():
    try:
        part_id = pid(request.form.get("partID"))
        rdate = dt(request.form.get("regDate"), "Reg date")
        # SKILLS TEST: Change payment mode values if exam requires different options
        mode = pm(request.form.get("regPMode"))
        with db() as c:
            # SKILLS TEST: JOIN to get data from both parent tables for computation
            row = c.execute(
                """SELECT p.partDRate, e.evRFee FROM Participants p
                   JOIN Events e ON p.evCode=e.evCode WHERE p.partID=?""",
                (part_id,),
            ).fetchone()
            if not row:
                raise ValueError("Participant not found")
            # SKILLS TEST: COMPUTED FIELD — change this formula for your exam
            # Current: fee_paid = event_fee - participant_discount
            paid = float(row["evRFee"]) - float(row["partDRate"])
            if paid < 0:
                raise ValueError("Discount > fee")
            c.execute(
                "INSERT INTO Registration (partID,regDate,regFPaid,regPMode) VALUES (?,?,?,?)",
                (part_id, rdate, paid, mode),
            )
        flash(f"Registered. Fee paid: {paid:.2f}", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except (sqlite3.Error, OSError) as e:
        flash(str(e), "danger")
    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    # SKILLS TEST: Change port number if exam requires a different one
    app.run(debug=True, port=5000)
