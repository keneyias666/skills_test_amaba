# ============================================================================
# SKILLS TEST CHEAT SHEET — Election Database Helper (dbhelper.py)
# ============================================================================
# All database operations for the Election/Voting system.
# Tables: Positions, Candidates, Voters, Votes
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. DB_NAME       — change "Election.db" to your exam's database filename
# 2. TABLE NAMES   — change Positions/Candidates/Voters/Votes in all SQL
# 3. COLUMN NAMES  — change posID/posName/candFName/voterID etc. in all SQL
# 4. STATUS VALUES — "active"/"inactive" can be changed
# 5. VOTE FLAG     — "y"/"n" for voted column can be changed
# 6. RESULTS LOGIC — percentage calculation and winner selection
#
# KEY PATTERNS:
#   - Every function: connect() → execute SQL → commit → close
#   - Row factory = sqlite3.Row (access columns by name, e.g., row["posID"])
#   - Foreign keys ON for referential integrity
#   - Soft delete = UPDATE SET status = 'inactive' (not DELETE)
# ============================================================================

import os
import sqlite3

# SKILLS TEST: Change DB filename and path as needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Election.db")


def connect():
    """
    SKILLS TEST: Database connection helper.
    - row_factory = sqlite3.Row enables dict-like access: row["column_name"]
    - PRAGMA foreign_keys = ON enforces FK constraints
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def person_name(first, middle, last):
    """
    SKILLS TEST: Concatenates name parts into a full name string.
    Use in templates: {{ person_name(row.fName, row.mName, row.lName) }}
    Change parameter names if exam uses different name columns.
    """
    parts = []
    for part in (first, middle, last):
        if part and str(part).strip():
            parts.append(str(part).strip())
    return " ".join(parts)


# ============================================================================
# SKILLS TEST: DASHBOARD COUNTS — Returns counts for the home page
# Change table names and conditions to match your exam.
# ============================================================================
def get_counts():
    conn = connect()
    counts = {
        "positions": conn.execute("SELECT COUNT(*) FROM Positions").fetchone()[0],
        "candidates": conn.execute("SELECT COUNT(*) FROM Candidates").fetchone()[0],
        "voters": conn.execute("SELECT COUNT(*) FROM Voters").fetchone()[0],
        # SKILLS TEST: Count voters who have already voted (voted = 'y')
        "ballots": conn.execute(
            "SELECT COUNT(*) FROM Voters WHERE voted = 'y'"
        ).fetchone()[0],
    }
    conn.close()
    return counts


# ============================================================================
# SKILLS TEST: POSITIONS CRUD
# Simple CRUD with no foreign key dependencies on insert.
# Deactivate = soft delete (UPDATE status, not DELETE).
# Change table name, column names, and ORDER BY to match exam.
# ============================================================================
def get_positions():
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM Positions ORDER BY posID"
    ).fetchall()
    conn.close()
    return rows


def get_position(pos_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM Positions WHERE posID = ?",
        (pos_id,),
    ).fetchone()
    conn.close()
    return row


# SKILLS TEST: INSERT — change column names and table name
def add_position(pos_name, num_of_positions, pos_stat):
    conn = connect()
    conn.execute(
        """
        INSERT INTO Positions (posName, numOfPositions, posStat)
        VALUES (?, ?, ?)
        """,
        (pos_name, num_of_positions, pos_stat),
    )
    conn.commit()
    conn.close()


# SKILLS TEST: UPDATE — change column names, table name, and WHERE clause
def update_position(pos_id, pos_name, num_of_positions, pos_stat):
    conn = connect()
    conn.execute(
        """
        UPDATE Positions
        SET posName = ?, numOfPositions = ?, posStat = ?
        WHERE posID = ?
        """,
        (pos_name, num_of_positions, pos_stat, pos_id),
    )
    conn.commit()
    conn.close()


# SKILLS TEST: DEACTIVATE (soft delete) — change table and column names
def deactivate_position(pos_id):
    conn = connect()
    conn.execute(
        "UPDATE Positions SET posStat = 'inactive' WHERE posID = ?",
        (pos_id,),
    )
    conn.commit()
    conn.close()


# ============================================================================
# SKILLS TEST: CANDIDATES CRUD
# Candidates reference Positions via foreign key (posID).
# get_candidates() uses a JOIN to include the position name in results.
# Change table names, column names, and JOIN conditions.
# ============================================================================
def get_candidates():
    conn = connect()
    # SKILLS TEST: JOIN pattern — pull data from parent table (Positions)
    rows = conn.execute(
        """
        SELECT c.*, p.posName
        FROM Candidates c
        JOIN Positions p ON p.posID = c.posID
        ORDER BY p.posID, c.candLName, c.candFName
        """
    ).fetchall()
    conn.close()
    return rows


def get_candidate(cand_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM Candidates WHERE candID = ?",
        (cand_id,),
    ).fetchone()
    conn.close()
    return row


# SKILLS TEST: INSERT with FK validation
# IntegrityError = invalid foreign key (position doesn't exist)
def add_candidate(first, middle, last, pos_id, cand_stat):
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO Candidates
                (candFName, candMName, candLName, posID, candStat)
            VALUES (?, ?, ?, ?, ?)
            """,
            (first, middle, last, pos_id, cand_stat),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Select a valid position.")
    finally:
        conn.close()


# SKILLS TEST: UPDATE with business rule — can't change position if votes exist
# This prevents data corruption. Change the business rule for your exam.
def update_candidate(cand_id, first, middle, last, pos_id, cand_stat):
    conn = connect()
    try:
        current = conn.execute(
            "SELECT posID FROM Candidates WHERE candID = ?",
            (cand_id,),
        ).fetchone()
        if current is None:
            raise ValueError("Candidate not found.")
        # SKILLS TEST: Business rule — prevent position change if votes exist
        if current["posID"] != int(pos_id):
            vote_count = conn.execute(
                "SELECT COUNT(*) FROM Votes WHERE candID = ?",
                (cand_id,),
            ).fetchone()[0]
            if vote_count:
                raise ValueError(
                    "This candidate already has votes, so the position cannot be changed."
                )
        conn.execute(
            """
            UPDATE Candidates
            SET candFName = ?, candMName = ?, candLName = ?, posID = ?, candStat = ?
            WHERE candID = ?
            """,
            (first, middle, last, pos_id, cand_stat, cand_id),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("Select a valid position.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def deactivate_candidate(cand_id):
    conn = connect()
    conn.execute(
        "UPDATE Candidates SET candStat = 'inactive' WHERE candID = ?",
        (cand_id,),
    )
    conn.commit()
    conn.close()


# ============================================================================
# SKILLS TEST: VOTERS CRUD
# Voters have a TEXT primary key (voterID) — not auto-increment.
# Voters have a password field for authentication.
# The "voted" column tracks if they've already voted ('y'/'n').
# Change table/column names and PK type for your exam.
# ============================================================================
def get_voters():
    conn = connect()
    rows = conn.execute(
        "SELECT * FROM Voters ORDER BY voterID"
    ).fetchall()
    conn.close()
    return rows


def get_voter(voter_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM Voters WHERE voterID = ?",
        (voter_id,),
    ).fetchone()
    conn.close()
    return row


# SKILLS TEST: INSERT voter — voted defaults to 'n'
# IntegrityError = duplicate voterID
def add_voter(voter_id, voter_pass, first, middle, last, voter_stat):
    conn = connect()
    try:
        conn.execute(
            """
            INSERT INTO Voters
                (voterID, voterPass, voterFName, voterMName, voterLName, voterStat, voted)
            VALUES (?, ?, ?, ?, ?, ?, 'n')
            """,
            (voter_id, voter_pass, first, middle, last, voter_stat),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("That voter ID is already in use.")
    finally:
        conn.close()


def update_voter(voter_id, voter_pass, first, middle, last, voter_stat):
    conn = connect()
    conn.execute(
        """
        UPDATE Voters
        SET voterPass = ?, voterFName = ?, voterMName = ?, voterLName = ?, voterStat = ?
        WHERE voterID = ?
        """,
        (voter_pass, first, middle, last, voter_stat, voter_id),
    )
    conn.commit()
    conn.close()


def deactivate_voter(voter_id):
    conn = connect()
    conn.execute(
        "UPDATE Voters SET voterStat = 'inactive' WHERE voterID = ?",
        (voter_id,),
    )
    conn.commit()
    conn.close()


# ============================================================================
# SKILLS TEST: AUTHENTICATION
# Checks voterID + voterPass in the database.
# Returns the voter row if valid, None if invalid.
# SKILLS TEST: Change column names if exam uses different login fields.
# ============================================================================
def authenticate(voter_id, voter_pass):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM Voters WHERE voterID = ? AND voterPass = ?",
        (voter_id, voter_pass),
    ).fetchone()
    conn.close()
    return row


# ============================================================================
# SKILLS TEST: BALLOT GENERATION
# Builds the voting form data: active positions + their active candidates.
# Returns a list of dicts: [{"position": {...}, "candidates": [...]}, ...]
# ============================================================================
def get_ballot():
    conn = connect()
    # SKILLS TEST: Only active positions appear on the ballot
    positions = conn.execute(
        """
        SELECT * FROM Positions
        WHERE posStat = 'active'
        ORDER BY posID
        """
    ).fetchall()
    ballot = []
    for position in positions:
        # SKILLS TEST: Only active candidates for each position
        candidates = conn.execute(
            """
            SELECT * FROM Candidates
            WHERE posID = ? AND candStat = 'active'
            ORDER BY candLName, candFName
            """,
            (position["posID"],),
        ).fetchall()
        ballot.append({"position": position, "candidates": candidates})
    conn.close()
    return ballot


# ============================================================================
# SKILLS TEST: CAST VOTES — The most complex database operation
# This is a TRANSACTION: all votes succeed or all fail.
# Validates:
#   1. Voter exists, is active, and hasn't voted yet
#   2. At least one selection made
#   3. No duplicate selections
#   4. Position is active
#   5. Number of selections doesn't exceed seat count
#   6. Each candidate is valid and active for that position
# Then INSERTs all votes and marks voter as voted.
# SKILLS TEST: Study this carefully — it's the most likely to need adaptation.
# ============================================================================
def cast_votes(voter_id, selections):
    conn = connect()
    try:
        voter = conn.execute(
            "SELECT * FROM Voters WHERE voterID = ?",
            (voter_id,),
        ).fetchone()
        if voter is None:
            raise ValueError("Voter not found.")
        if voter["voterStat"] != "active":
            raise ValueError("Your account is inactive. You cannot vote.")
        if voter["voted"] == "y":
            raise ValueError("You have already voted.")
        if not selections:
            raise ValueError("Select at least one candidate.")

        # SKILLS TEST: Group selections by position for validation
        grouped = {}
        for pos_id, cand_id in selections:
            grouped.setdefault(int(pos_id), []).append(int(cand_id))

        # SKILLS TEST: Validate each position's selections
        for pos_id, cand_ids in grouped.items():
            # No duplicate candidate selections
            if len(cand_ids) != len(set(cand_ids)):
                raise ValueError("A candidate was selected more than once.")
            position = conn.execute(
                "SELECT * FROM Positions WHERE posID = ?",
                (pos_id,),
            ).fetchone()
            if position is None or position["posStat"] != "active":
                raise ValueError("That position is not open for voting.")
            # SKILLS TEST: Seat limit check — can't vote for more candidates than seats
            if len(cand_ids) > position["numOfPositions"]:
                raise ValueError(
                    "You may vote for at most "
                    f"{position['numOfPositions']} candidate(s) for {position['posName']}."
                )
            # Verify each candidate is valid
            for cand_id in cand_ids:
                candidate = conn.execute(
                    """
                    SELECT candID FROM Candidates
                    WHERE candID = ? AND posID = ? AND candStat = 'active'
                    """,
                    (cand_id, pos_id),
                ).fetchone()
                if candidate is None:
                    raise ValueError("One of the selected candidates is not available.")

        # SKILLS TEST: INSERT all votes + mark voter as voted (atomic transaction)
        try:
            for pos_id, cand_ids in grouped.items():
                for cand_id in cand_ids:
                    conn.execute(
                        """
                        INSERT INTO Votes (posID, voterID, candID)
                        VALUES (?, ?, ?)
                        """,
                        (pos_id, voter_id, cand_id),
                    )
            # SKILLS TEST: Mark voter as voted — uses WHERE conditions to prevent race
            updated = conn.execute(
                """
                UPDATE Voters
                SET voted = 'y'
                WHERE voterID = ? AND voted = 'n' AND voterStat = 'active'
                """,
                (voter_id,),
            )
            if updated.rowcount != 1:
                raise ValueError("You have already voted.")
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError("Your ballot could not be saved.")
        except Exception:
            conn.rollback()
            raise
    finally:
        conn.close()


# ============================================================================
# SKILLS TEST: RESULTS — Vote counts and percentages
# Uses LEFT JOIN to include candidates with zero votes.
# Groups by position, then computes percentage for each candidate.
# Returns: [{posID, posName, candidates: [{name, totalVotes, percentage}]}]
# SKILLS TEST: Change the GROUP BY query if exam has different aggregation.
# ============================================================================
def get_results():
    conn = connect()
    rows = conn.execute(
        """
        SELECT
            p.posID,
            p.posName,
            p.numOfPositions,
            p.posStat,
            c.candID,
            c.candFName,
            c.candMName,
            c.candLName,
            c.candStat,
            COUNT(v.candID) AS totalVotes
        FROM Positions p
        LEFT JOIN Candidates c ON c.posID = p.posID
        LEFT JOIN Votes v ON v.candID = c.candID AND v.posID = p.posID
        GROUP BY p.posID, c.candID
        ORDER BY p.posID, totalVotes DESC, c.candLName, c.candFName
        """
    ).fetchall()
    conn.close()

    # SKILLS TEST: Transform flat rows into nested structure for templates
    blocks = []
    index = {}
    for row in rows:
        pos_id = row["posID"]
        if pos_id not in index:
            block = {
                "posID": pos_id,
                "posName": row["posName"],
                "numOfPositions": row["numOfPositions"],
                "posStat": row["posStat"],
                "candidates": [],
                "votesCast": 0,
            }
            index[pos_id] = block
            blocks.append(block)
        if row["candID"] is None:
            continue
        block = index[pos_id]
        total_votes = row["totalVotes"]
        block["votesCast"] += total_votes
        block["candidates"].append(
            {
                "candID": row["candID"],
                "name": person_name(row["candFName"], row["candMName"], row["candLName"]),
                "candStat": row["candStat"],
                "totalVotes": total_votes,
            }
        )

    # SKILLS TEST: PERCENTAGE CALCULATION
    # percentage = (candidate_votes / total_votes_for_position) * 100
    for block in blocks:
        total = block["votesCast"]
        for candidate in block["candidates"]:
            if total:
                candidate["percentage"] = round(candidate["totalVotes"] * 100 / total, 2)
            else:
                candidate["percentage"] = 0
    return blocks


# ============================================================================
# SKILLS TEST: WINNERS — Top N candidates per position
# N = numOfPositions (number of seats for that position)
# Uses Python list slicing: candidates[:numOfPositions]
# Candidates are already sorted by totalVotes DESC from get_results()
# ============================================================================
def get_winners():
    winners = []
    for block in get_results():
        # SKILLS TEST: Slice the top candidates based on seat count
        seated = block["candidates"][: block["numOfPositions"]]
        for candidate in seated:
            winners.append(
                {
                    "posName": block["posName"],
                    "name": candidate["name"],
                    "totalVotes": candidate["totalVotes"],
                }
            )
    return winners

