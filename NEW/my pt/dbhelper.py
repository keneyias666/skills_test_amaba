# ============================================================================
# SKILLS TEST CHEAT SHEET — Pet Clinic Database Helper (dbhelper.py)
# ============================================================================
# All database operations for the Pet Clinic system.
# Tables: Veterinarian, PetOwner, Pet, Consultation
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. TABLE NAMES    — change Veterinarian/PetOwner/Pet/Consultation in SQL
# 2. COLUMN NAMES   — change vetID/petOwnerFName/petName etc. in SQL
# 3. SOFT DELETE    — "is_deleted = 0" filter on every query (WHERE is_deleted = 0)
#                     Remove if exam uses hard delete (DELETE FROM)
# 4. SEARCH FIELDS  — change LIKE columns in search_*() functions
# 5. JOIN QUERIES   — change JOIN conditions for related table lookups
# 6. REPORT QUERIES — change the 5 inquiry functions at the bottom
#
# KEY PATTERNS:
#   - _execute() for INSERT/UPDATE (no return value)
#   - _fetchall() for SELECT multiple rows (returns list of dicts)
#   - _fetchone() for SELECT single row (returns dict or None)
#   - Every query filters with "is_deleted = 0" for soft delete
#   - dict(row) converts sqlite3.Row to Python dict
# ============================================================================

from typing import Any, Dict, List, Optional

from database import get_connection


# ============================================================================
# SKILLS TEST: GENERIC HELPERS — Reuse these for any table
# These 3 functions wrap all database operations. You rarely need to change them.
# ============================================================================

def _execute(query: str, params: tuple = ()) -> None:
    """Execute INSERT/UPDATE/DELETE. No return value."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()


def _fetchall(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute SELECT and return ALL matching rows as list of dicts."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def _fetchone(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute SELECT and return ONE row as dict, or None if not found."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================================================
# SKILLS TEST: VETERINARIAN CRUD
# Change table name, column names, and parameter names to match your exam.
# Pattern: create → update → logical_delete → get → search
# ============================================================================

# SKILLS TEST: INSERT — change column names and table name
def create_vet(data: Dict[str, Any]) -> None:
    _execute(
        """
        INSERT INTO Veterinarian (vetID, vetFName, vetLName, vetAddress, vetSpecial)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["vetID"],
            data["vetFName"],
            data["vetLName"],
            data["vetAddress"],
            data["vetSpecial"],
        ),
    )


# SKILLS TEST: UPDATE — change SET columns and WHERE clause
# Note: "AND is_deleted = 0" prevents updating deleted records
def update_vet(vet_id: str, data: Dict[str, Any]) -> None:
    _execute(
        """
        UPDATE Veterinarian
        SET vetFName = ?, vetLName = ?, vetAddress = ?, vetSpecial = ?
        WHERE vetID = ? AND is_deleted = 0
        """,
        (
            data["vetFName"],
            data["vetLName"],
            data["vetAddress"],
            data["vetSpecial"],
            vet_id,
        ),
    )


# SKILLS TEST: LOGICAL (SOFT) DELETE — sets is_deleted = 1 instead of DELETE FROM
# To use HARD delete instead: _execute("DELETE FROM Veterinarian WHERE vetID = ?", (vet_id,))
def logical_delete_vet(vet_id: str) -> None:
    _execute("UPDATE Veterinarian SET is_deleted = 1 WHERE vetID = ?", (vet_id,))


# SKILLS TEST: GET ONE — fetch single record by primary key
# "AND is_deleted = 0" excludes soft-deleted records
def get_vet(vet_id: str) -> Optional[Dict[str, Any]]:
    return _fetchone(
        "SELECT * FROM Veterinarian WHERE vetID = ? AND is_deleted = 0", (vet_id,)
    )


# SKILLS TEST: SEARCH — fetch records matching a keyword
# Uses LIKE '%keyword%' for partial matching across multiple columns.
# Change the LIKE columns to match your exam's searchable fields.
def search_vets(keyword: str = "") -> List[Dict[str, Any]]:
    if not keyword:
        return _fetchall("SELECT * FROM Veterinarian WHERE is_deleted = 0 ORDER BY vetLName")
    like = f"%{keyword}%"
    return _fetchall(
        """
        SELECT * FROM Veterinarian
        WHERE is_deleted = 0
          AND (vetID LIKE ? OR vetFName LIKE ? OR vetLName LIKE ? OR vetSpecial LIKE ?)
        ORDER BY vetLName
        """,
        (like, like, like, like),
    )


# ============================================================================
# SKILLS TEST: PET OWNER CRUD — Same pattern as Veterinarian
# Change table name, column names, and searchable fields.
# ============================================================================

def create_owner(data: Dict[str, Any]) -> None:
    _execute(
        """
        INSERT INTO PetOwner (petOwnerID, petOwnerFName, petOwnerLName, petOwnerBDate, petOwnerTelNo)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["petOwnerID"],
            data["petOwnerFName"],
            data["petOwnerLName"],
            data["petOwnerBDate"],
            data["petOwnerTelNo"],
        ),
    )


def update_owner(owner_id: str, data: Dict[str, Any]) -> None:
    _execute(
        """
        UPDATE PetOwner
        SET petOwnerFName = ?, petOwnerLName = ?, petOwnerBDate = ?, petOwnerTelNo = ?
        WHERE petOwnerID = ? AND is_deleted = 0
        """,
        (
            data["petOwnerFName"],
            data["petOwnerLName"],
            data["petOwnerBDate"],
            data["petOwnerTelNo"],
            owner_id,
        ),
    )


def logical_delete_owner(owner_id: str) -> None:
    _execute("UPDATE PetOwner SET is_deleted = 1 WHERE petOwnerID = ?", (owner_id,))


def get_owner(owner_id: str):
    return _fetchone(
        "SELECT * FROM PetOwner WHERE petOwnerID = ? AND is_deleted = 0", (owner_id,)
    )


def search_owners(keyword: str = "") -> List[Dict[str, Any]]:
    if not keyword:
        return _fetchall("SELECT * FROM PetOwner WHERE is_deleted = 0 ORDER BY petOwnerLName")
    like = f"%{keyword}%"
    return _fetchall(
        """
        SELECT * FROM PetOwner
        WHERE is_deleted = 0
          AND (petOwnerID LIKE ? OR petOwnerFName LIKE ? OR petOwnerLName LIKE ?)
        ORDER BY petOwnerLName
        """,
        (like, like, like),
    )


# ============================================================================
# SKILLS TEST: PET CRUD — Child of PetOwner (has foreign key petOwnerID)
# search_pets() uses a LEFT JOIN to include owner name in results.
# Change table names, column names, and JOIN conditions.
# ============================================================================

def create_pet(data: Dict[str, Any]) -> None:
    _execute(
        """
        INSERT INTO Pet (petID, petName, petType, petSex, petBDate, petOwnerID)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["petID"],
            data["petName"],
            data["petType"],
            data["petSex"],
            data["petBDate"],
            data["petOwnerID"],
        ),
    )


def update_pet(pet_id: str, data: Dict[str, Any]) -> None:
    _execute(
        """
        UPDATE Pet
        SET petName = ?, petType = ?, petSex = ?, petBDate = ?, petOwnerID = ?
        WHERE petID = ? AND is_deleted = 0
        """,
        (
            data["petName"],
            data["petType"],
            data["petSex"],
            data["petBDate"],
            data["petOwnerID"],
            pet_id,
        ),
    )


def logical_delete_pet(pet_id: str) -> None:
    _execute("UPDATE Pet SET is_deleted = 1 WHERE petID = ?", (pet_id,))


def get_pet(pet_id: str):
    return _fetchone("SELECT * FROM Pet WHERE petID = ? AND is_deleted = 0", (pet_id,))


# SKILLS TEST: SEARCH with JOIN — pulls owner name from PetOwner table
# LEFT JOIN = include pets even if owner is missing/deleted
# Change JOIN condition and LIKE columns for your exam.
def search_pets(keyword: str = "") -> List[Dict[str, Any]]:
    if not keyword:
        return _fetchall(
            """
            SELECT P.*, O.petOwnerFName, O.petOwnerLName
            FROM Pet P
            LEFT JOIN PetOwner O ON P.petOwnerID = O.petOwnerID
            WHERE P.is_deleted = 0
            ORDER BY P.petName
            """
        )
    like = f"%{keyword}%"
    return _fetchall(
        """
        SELECT P.*, O.petOwnerFName, O.petOwnerLName
        FROM Pet P
        LEFT JOIN PetOwner O ON P.petOwnerID = O.petOwnerID
        WHERE P.is_deleted = 0
          AND (P.petID LIKE ? OR P.petName LIKE ? OR O.petOwnerFName LIKE ? OR O.petOwnerLName LIKE ?)
        ORDER BY P.petName
        """,
        (like, like, like, like),
    )


# ============================================================================
# SKILLS TEST: CONSULTATION CRUD — Transaction linking Pet + Veterinarian
# Has TWO foreign keys: petID → Pet, vetID → Veterinarian
# search_consultations() joins both Pet and Veterinarian for display.
# Change table names, column names, and JOIN conditions.
# ============================================================================

def create_consultation(data: Dict[str, Any]) -> None:
    _execute(
        """
        INSERT INTO Consultation (consultID, petID, vetID, consultDate, diagnoses, prescription)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["consultID"],
            data["petID"],
            data["vetID"],
            data["consultDate"],
            data["diagnoses"],
            data["prescription"],
        ),
    )


def update_consultation(consult_id: str, data: Dict[str, Any]) -> None:
    _execute(
        """
        UPDATE Consultation
        SET petID = ?, vetID = ?, consultDate = ?, diagnoses = ?, prescription = ?
        WHERE consultID = ? AND is_deleted = 0
        """,
        (
            data["petID"],
            data["vetID"],
            data["consultDate"],
            data["diagnoses"],
            data["prescription"],
            consult_id,
        ),
    )


def logical_delete_consultation(consult_id: str) -> None:
    _execute("UPDATE Consultation SET is_deleted = 1 WHERE consultID = ?", (consult_id,))


def get_consultation(consult_id: str):
    return _fetchone(
        "SELECT * FROM Consultation WHERE consultID = ? AND is_deleted = 0",
        (consult_id,),
    )


# SKILLS TEST: SEARCH with DOUBLE JOIN — pulls pet name + vet name
def search_consultations(keyword: str = "") -> List[Dict[str, Any]]:
    if not keyword:
        return _fetchall(
            """
            SELECT C.*, P.petName, V.vetFName, V.vetLName
            FROM Consultation C
            LEFT JOIN Pet P ON C.petID = P.petID
            LEFT JOIN Veterinarian V ON C.vetID = V.vetID
            WHERE C.is_deleted = 0
            ORDER BY C.consultDate DESC
            """
        )
    like = f"%{keyword}%"
    return _fetchall(
        """
        SELECT C.*, P.petName, V.vetFName, V.vetLName
        FROM Consultation C
        LEFT JOIN Pet P ON C.petID = P.petID
        LEFT JOIN Veterinarian V ON C.vetID = V.vetID
        WHERE C.is_deleted = 0
          AND (C.consultID LIKE ? OR C.petID LIKE ? OR C.vetID LIKE ?)
        ORDER BY C.consultDate DESC
        """,
        (like, like, like),
    )


# ============================================================================
# SKILLS TEST: INQUIRY / REPORT QUERIES
# These are specialized read-only queries for the reports page.
# Each returns a filtered list of records based on user input.
#
# WHAT TO CHANGE:
# 1. Change table/column names in SELECT, JOIN, WHERE clauses
# 2. Change the filter criteria (WHERE conditions)
# 3. Add new inquiry types if exam requires different reports
# 4. Change ORDER BY to match exam requirements
# ============================================================================

# SKILLS TEST: REPORT 1 — Find vets by specialization (partial match)
def vets_by_specialization(special: str):
    like = f"%{special}%"
    return _fetchall(
        """
        SELECT vetID,
               vetFName,
               vetLName,
               vetSpecial
        FROM   Veterinarian
        WHERE  is_deleted = 0
           AND vetSpecial LIKE ?
        ORDER BY vetSpecial, vetLName
        """,
        (like,),
    )


# SKILLS TEST: REPORT 2 — Find consultations for a specific pet
def consultations_by_pet(pet_id: str):
    return _fetchall(
        """
        SELECT C.consultID,
               C.consultDate,
               C.diagnoses,
               C.prescription,
               P.petID,
               P.petName,
               V.vetID,
               V.vetFName,
               V.vetLName
        FROM   Consultation C
        JOIN   Pet P
               ON C.petID = P.petID
        JOIN   Veterinarian V
               ON C.vetID = V.vetID
        WHERE  C.is_deleted = 0
           AND C.petID = ?
        ORDER BY C.consultDate DESC
        """,
        (pet_id,),
    )


# SKILLS TEST: REPORT 3 — Find consultations for a specific pet owner
# Uses a 3-table JOIN: Consultation → Pet → PetOwner
def consultations_by_owner(owner_id: str):
    return _fetchall(
        """
        SELECT C.consultID,
               C.consultDate,
               C.diagnoses,
               C.prescription,
               P.petID,
               P.petName,
               O.petOwnerID,
               O.petOwnerFName,
               O.petOwnerLName,
               V.vetID,
               V.vetFName,
               V.vetLName
        FROM   Consultation C
        JOIN   Pet P
               ON C.petID = P.petID
        JOIN   PetOwner O
               ON P.petOwnerID = O.petOwnerID
        JOIN   Veterinarian V
               ON C.vetID = V.vetID
        WHERE  C.is_deleted = 0
           AND O.petOwnerID = ?
        ORDER BY C.consultDate DESC
        """,
        (owner_id,),
    )


# SKILLS TEST: REPORT 4 — Find consultations for a specific vet
def consultations_by_vet(vet_id: str):
    return _fetchall(
        """
        SELECT C.consultID,
               C.consultDate,
               C.diagnoses,
               C.prescription,
               P.petID,
               P.petName,
               V.vetID,
               V.vetFName,
               V.vetLName
        FROM   Consultation C
        JOIN   Pet P
               ON C.petID = P.petID
        JOIN   Veterinarian V
               ON C.vetID = V.vetID
        WHERE  C.is_deleted = 0
           AND C.vetID = ?
        ORDER BY C.consultDate DESC
        """,
        (vet_id,),
    )


# SKILLS TEST: REPORT 5 — Find consultations within a date range
# Uses SQLite date() function: date(C.consultDate) BETWEEN date(?) AND date(?)
# Dates must be in YYYY-MM-DD format for this to work correctly.
def consultations_between_dates(date_from: str, date_to: str):
    return _fetchall(
        """
        SELECT C.consultID,
               C.consultDate,
               C.diagnoses,
               C.prescription,
               P.petID,
               P.petName,
               O.petOwnerID,
               O.petOwnerFName,
               O.petOwnerLName,
               V.vetID,
               V.vetFName,
               V.vetLName
        FROM   Consultation C
        JOIN   Pet P
               ON C.petID = P.petID
        JOIN   PetOwner O
               ON P.petOwnerID = O.petOwnerID
        JOIN   Veterinarian V
               ON C.vetID = V.vetID
        WHERE  C.is_deleted = 0
           AND date(C.consultDate) BETWEEN date(?) AND date(?)
        ORDER BY C.consultDate DESC
        """,
        (date_from, date_to),
    )


