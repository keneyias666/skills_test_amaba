# ============================================================================
# SKILLS TEST CHEAT SHEET — Book Inventory Database Helper (dbhelper.py)
# ============================================================================
# This file handles ALL database operations for the Books system.
# Each function = one SQL operation. Copy and rename for new tables.
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. DB_NAME       — change "books.db" to your exam's database filename
# 2. TABLE NAME    — change "books" in every SQL statement
# 3. COLUMN NAMES  — change isbn/title/copyright/edition/price/quantity
# 4. COLUMN TYPES  — INTEGER, TEXT, REAL — adjust to match exam schema
# 5. PRIMARY KEY   — "isbn INTEGER PRIMARY KEY" can be AUTOINCREMENT if needed
# 6. SEED DATA     — change the sample rows in seed_data()
# 7. TOTAL FORMULA — change "price * quantity" in get_all() if exam differs
# 8. VALIDATION    — add field checks in update_book() as exam requires
# ============================================================================

import sqlite3

# SKILLS TEST: Change this to your exam's database filename
DB_NAME = "books.db"


def connect():
    """Create and return a database connection. No changes typically needed."""
    return sqlite3.connect(DB_NAME)


def create_table():
    """
    SKILLS TEST: Create the main table.
    Change table name, column names, and types to match your exam.
    - INTEGER PRIMARY KEY = auto-generated numeric key (or manual if no AUTOINCREMENT)
    - TEXT = string fields
    - REAL = decimal/float fields (prices, rates, scores)
    - INTEGER = whole number fields (quantity, age, count)
    - Add NOT NULL if the exam requires mandatory fields
    - Add UNIQUE if the exam requires unique values
    - Add DEFAULT if the exam requires default values
    - Add CHECK constraints if the exam requires value restrictions
    """
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Rename "books" and all columns below
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        isbn INTEGER PRIMARY KEY,
        title TEXT,
        copyright TEXT,
        edition TEXT,
        price REAL,
        quantity INTEGER
    )
    """)

    conn.commit()
    conn.close()


# SKILLS TEST: ADD / INSERT — Creates a new record
# Change parameter names and SQL column names to match your exam.
# The bare except catches duplicate primary key errors.
def add_book(isbn, title, copyright, edition, price, quantity):
    conn = connect()
    cursor = conn.cursor()

    try:
        # SKILLS TEST: Change table name and column count (? placeholders)
        cursor.execute("""
        INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)
        """, (int(isbn), title, copyright, edition, float(price), int(quantity)))

        conn.commit()
        return "Book added successfully"

    except:
        # SKILLS TEST: This catches duplicate primary key errors
        return "ISBN already exists"

    finally:
        conn.close()


# SKILLS TEST: SEARCH / GET ONE — Fetches a single record by primary key
# Change table name and WHERE column to match your exam.
def get_book(isbn):
    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Change "books" and "isbn" to your table/PK column
    cursor.execute("SELECT * FROM books WHERE isbn=?", (isbn,))
    data = cursor.fetchone()

    conn.close()
    return data


# SKILLS TEST: GET ALL + TOTAL — Fetches all records and computes an aggregate
# The total calculation is: sum of (price * quantity) for every row.
# Change the formula if exam requires different aggregation:
#   e.g., sum of scores, average of grades, count of items, etc.
def get_all():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    # SKILLS TEST: AGGREGATE CALCULATION — Change indices and formula
    # r[4] = price (5th column, 0-indexed), r[5] = quantity (6th column)
    # If your columns are in different positions, change the indices!
    total = sum(float(r[4]) * int(r[5]) for r in rows)

    conn.close()
    return rows, total


# SKILLS TEST: UPDATE — Modifies an existing record
# Change parameter names, SQL SET columns, and WHERE clause.
# Includes basic validation: all fields must be non-empty.
def update_book(isbn, title, copyright, edition, price, quantity):
    # SKILLS TEST: Validation — check all required fields
    # Add/remove field checks as your exam requires
    if not title or not copyright or not edition or not price or not quantity:
        return "All fields are required"

    conn = connect()
    cursor = conn.cursor()

    # SKILLS TEST: Change "books", SET columns, and WHERE column
    cursor.execute("""
    UPDATE books
    SET title=?, copyright=?, edition=?, price=?, quantity=?
    WHERE isbn=?
    """, (
        title,
        copyright,
        edition,
        float(price),
        int(quantity),
        int(isbn)
    ))

    conn.commit()
    conn.close()

    return "Book updated successfully"


# SKILLS TEST: DELETE — Removes a record by primary key
# Change table name and WHERE column.
# NOTE: This is a HARD delete (permanent). For soft/logical delete,
# add an "is_deleted" column and UPDATE it to 1 instead of DELETE.
def delete_book(isbn):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE isbn=?", (isbn,))

    conn.commit()
    conn.close()

    return "Book deleted"


# SKILLS TEST: SEED DATA — Pre-populates the table with sample records
# Change the data to match your exam's requirements.
# The "if count == 0" check prevents re-inserting if data already exists.
def seed_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]

    if count == 0:
        # SKILLS TEST: Change these rows to match your exam's sample data
        # Format: (primary_key, field1, field2, field3, numeric1, numeric2)
        books = [
            (1, "Harry Potter", "2005", "1st", 595.00, 3),
            (2, "Lord of the Rings", "2004", "3rd", 999.00, 10),
            (3, "Java Programming", "2010", "UPE", 549.00, 2),
            (4, "The Notebook", "1999", "US", 750.00, 11)
        ]

        cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", books)
        conn.commit()

    conn.close()