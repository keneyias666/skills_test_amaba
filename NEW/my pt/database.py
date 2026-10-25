# ============================================================================
# SKILLS TEST QUESTIONNAIRE: CLINICAL DATABASE ARCHITECTURE (database.py)
# ============================================================================
# EXAM SCENARIO: Database schema initialization and soft-deletion architecture.
#
# CANDIDATE TASKS & OBJECTIVES (WHAT NEEDS TO BE DONE):
# 1. 4-TABLE CLINICAL SCHEMA:
#    - PetOwner: petOwnerID (PK), ownerFName, ownerLName, ownerAddress,
#      ownerContact, is_deleted (DEFAULT 0).
#    - Veterinarian: vetID (PK), vetFName, vetLName, vetContact,
#      specialization, is_deleted (DEFAULT 0).
#    - Pet: petID (PK), petName, petType, petBreed, petBDate,
#      petOwnerID (FK -> PetOwner), is_deleted (DEFAULT 0).
#    - Consultation: consultID (PK AUTOINCREMENT), petID (FK -> Pet),
#      vetID (FK -> Veterinarian), consultDate, consultTime, diagnosis,
#      treatment, is_deleted (DEFAULT 0).
# 2. LOGICAL (SOFT) DELETION:
#    - All entities maintain history using "is_deleted" flags.
# ============================================================================

import sqlite3
from pathlib import Path


# SKILLS TEST: Change the database filename here
DB_PATH = Path(__file__).with_name("clinic.db")


def get_connection():
    """
    SKILLS TEST: Database connection helper.
    - timeout=10 prevents immediate failure when DB is locked
    - row_factory=sqlite3.Row enables dict-like access: row["column_name"]
    """
    # timeout gives SQLite some time to wait for a lock instead of failing immediately
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    SKILLS TEST: Create all tables if they don't exist.
    Change table names, column names, and types to match your exam.
    """
    conn = get_connection()
    cur = conn.cursor()

    # SKILLS TEST: TABLE 1 — PetOwner (entity with personal info)
    # Change "PetOwner" and all column names to match your exam
    # petOwnerID = TEXT primary key (manual entry, not auto-increment)
    # petOwnerBDate = date stored as TEXT in YYYY-MM-DD format
    # petOwnerTelNo = phone number as TEXT
    # is_deleted = soft-delete flag (0=active, 1=deleted)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS PetOwner (
            petOwnerID TEXT PRIMARY KEY,
            petOwnerFName TEXT NOT NULL,
            petOwnerLName TEXT NOT NULL,
            petOwnerBDate TEXT NOT NULL,
            petOwnerTelNo TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    # SKILLS TEST: TABLE 2 — Veterinarian (entity with specialization)
    # Change "Veterinarian" and all column names
    # vetSpecial = specialty/category field (e.g., "Surgery", "Dentistry")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Veterinarian (
            vetID TEXT PRIMARY KEY,
            vetFName TEXT NOT NULL,
            vetLName TEXT NOT NULL,
            vetAddress TEXT NOT NULL,
            vetSpecial TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    # SKILLS TEST: TABLE 3 — Pet (child of PetOwner via foreign key)
    # petSex = constrained text (e.g., "Male"/"Female")
    # petOwnerID = foreign key → PetOwner table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Pet (
            petID TEXT PRIMARY KEY,
            petName TEXT NOT NULL,
            petType TEXT NOT NULL,
            petSex TEXT NOT NULL,
            petBDate TEXT NOT NULL,
            petOwnerID TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (petOwnerID) REFERENCES PetOwner(petOwnerID)
        )
        """
    )

    # SKILLS TEST: TABLE 4 — Consultation (transaction linking Pet + Veterinarian)
    # Two foreign keys: petID → Pet, vetID → Veterinarian
    # consultDate = datetime stored as TEXT "YYYY-MM-DD HH:MM"
    # diagnoses, prescription = long text fields
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Consultation (
            consultID TEXT PRIMARY KEY,
            petID TEXT NOT NULL,
            vetID TEXT NOT NULL,
            consultDate TEXT NOT NULL,
            diagnoses TEXT NOT NULL,
            prescription TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (petID) REFERENCES Pet(petID),
            FOREIGN KEY (vetID) REFERENCES Veterinarian(vetID)
        )
        """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")


