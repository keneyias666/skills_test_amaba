# ============================================================================
# SKILLS TEST CHEAT SHEET — Book Inventory System (main.py)
# ============================================================================
# This is a SINGLE-TABLE Flask CRUD app: books
# All operations (Add, Search, Update, Delete) happen on ONE page (index.html).
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. TABLE NAME    — "books" → your exam's table name
# 2. COLUMN NAMES  — isbn/title/copyright/edition/price/quantity → your columns
# 3. DB FILENAME   — change "books.db" in dbhelper.py
# 4. ACTIONS       — "search", "add", "update", "delete" match hidden form field
# 5. FORM FIELDS   — request.form["title"] etc. must match HTML <input name="...">
# 6. TEMPLATE      — "index.html" can be renamed if exam requires
# 7. TOTAL CALC    — get_all() returns (rows, total) where total = sum(price*qty)
# 8. SEED DATA     — change the initial data in dbhelper.seed_data()
#
# PATTERN: Single-page app using POST actions to dispatch CRUD operations.
# ============================================================================

from flask import Flask, render_template, request
import dbhelper

app = Flask(__name__)

# SKILLS TEST: These run at startup — create the table and insert seed data.
# If the exam says "no seed data", remove dbhelper.seed_data()
dbhelper.create_table()
dbhelper.seed_data()


# SKILLS TEST: This single route handles EVERYTHING — listing, searching, adding, etc.
# The "action" hidden field in the HTML form determines which operation runs.
# If the exam wants separate pages, split this into multiple @app.route functions.
@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    book = None

    if request.method == "POST":
        # SKILLS TEST: "action" comes from a hidden <input name="action" value="search">
        # Change these action names if the exam uses different button names.
        action = request.form.get("action")

        # SKILLS TEST: "isbn" is the primary key field from the form
        # Change to your exam's primary key field name
        isbn = request.form.get("isbn")
        if isbn:
            isbn = int(isbn)

        # SKILLS TEST: SEARCH — fetches one record by primary key
        if action == "search":
            book = dbhelper.get_book(isbn)
            if not book:
                message = "ITEM NOT FOUND"
            else:
                message = "ITEM FOUND"

        # SKILLS TEST: ADD — inserts a new record
        # Change form field names (title, copyright, edition, price, quantity)
        # to match your exam's column names
        elif action == "add":
            message = dbhelper.add_book(
                isbn,
                request.form["title"],
                request.form["copyright"],
                request.form["edition"],
                request.form["price"],
                request.form["quantity"]
            )

        # SKILLS TEST: UPDATE — modifies an existing record
        # Same form fields as ADD; change to match exam
        elif action == "update":
            message = dbhelper.update_book(
                isbn,
                request.form["title"],
                request.form["copyright"],
                request.form["edition"],
                request.form["price"],
                request.form["quantity"]
            )

        # SKILLS TEST: DELETE — removes a record by primary key
        elif action == "delete":
            message = dbhelper.delete_book(isbn)

    # SKILLS TEST: get_all() returns TWO values: list of rows + computed total
    # "total" is the aggregate (sum of price * quantity for all books)
    # Change the aggregation formula in dbhelper.py if exam requires different calc
    books, total = dbhelper.get_all()

    # SKILLS TEST: Change template name and variable names if exam requires
    return render_template(
        "index.html",
        books=books,
        total=total,
        message=message,
        book=book
    )


if __name__ == "__main__":
    # SKILLS TEST: Change port by adding port=XXXX, e.g., app.run(debug=True, port=8080)
    app.run(debug=True)