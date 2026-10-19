# ============================================================================
# SKILLS TEST CHEAT SHEET — Pet Clinic Database Setup (database.py)
# ============================================================================
# This file creates the database and all 4 tables.
# Tables: PetOwner, Veterinarian, Pet, Consultation
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. DB_PATH       — change "clinic.db" to your exam's database filename
# 2. TABLE NAMES   — change PetOwner/Veterinarian/Pet/Consultation
# 3. COLUMN NAMES  — change petOwnerID/vetFName/petName etc.
# 4. COLUMN TYPES  — TEXT, INTEGER, REAL as needed
# 5. FOREIGN KEYS  — adjust REFERENCES between tables
# 6. is_deleted    — soft-delete flag (0=active, 1=deleted)
#                    Remove if exam uses hard delete (DELETE FROM)
#
# KEY PATTERN: Every table has "is_deleted INTEGER NOT NULL DEFAULT 0"
# for LOGICAL (soft) DELETE. Queries filter with "WHERE is_deleted = 0".
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


