# ============================================================================
# SKILLS TEST CHEAT SHEET — Student ID System (main.py)
# ============================================================================
# This is a SINGLE-TABLE Flask CRUD app: students
# Features: Add, Search, Edit, Delete students.
#
# WHAT TO CHANGE DURING A SKILLS TEST:
# 1. TABLE NAME     — "students" → your exam's table name
# 2. COLUMN NAMES   — student_id/name/course/score → your exam columns
# 3. DB FILENAME    — change "students.db" in dbhelper.py
# 4. FORM FIELDS    — request.form["name"] etc. must match HTML <input name="...">
# 5. ROUTES         — /, /edit/<id>, /delete/<id>
# 6. TEMPLATES      — index.html, edit.html
# 7. SEARCH FIELDS  — change LIKE columns in dbhelper.search_student()
# 8. DATE TRACKING  — date_added is auto-generated on insert
#
# PATTERN: Single-page listing with separate edit page.
# DELETE uses GET (no confirmation) — change to POST if exam requires.
# ============================================================================

from flask import Flask, render_template, request, redirect, url_for
import dbhelper

app = Flask(__name__)

# SKILLS TEST: Create table if not exists — runs at startup
dbhelper.create_table()


# ============================================================================
# SKILLS TEST: HOME ROUTE — Add + View + Search on one page
# GET: lists all students (or search results if ?search=keyword)
# POST: adds a new student record
# ============================================================================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # SKILLS TEST: Change form field names to match your HTML form
        student_id = request.form["student_id"]
        name = request.form["name"]
        course = request.form["course"]
        score = request.form["score"]
        
        try:
            dbhelper.add_student(student_id, name, course, score)
        except:
            pass  # SKILLS TEST: Silently ignores duplicate student_id errors

        return redirect(url_for("index"))

    # SKILLS TEST: Search — reads ?search=keyword from URL query string
    keyword = request.args.get("search")

    if keyword:
        students = dbhelper.search_student(keyword)
    else:
        students = dbhelper.get_all_students()

    return render_template("index.html", students=students)


# ============================================================================
# SKILLS TEST: EDIT ROUTE — Separate page for editing a record
# GET: loads the existing student record into an edit form
# POST: updates the record with new form data
# Note: "id" here is the auto-increment primary key, NOT student_id
# ============================================================================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    student = dbhelper.get_student(id)

    if request.method == "POST":
        # SKILLS TEST: Change form field names to match your HTML form
        name = request.form["name"]
        course = request.form["course"]
        score = request.form["score"]
        date_added = request.form["date_added"]
        dbhelper.update_student(id, name, course, score)
        return redirect(url_for("index"))

    return render_template("edit.html", student=student)

# ============================================================================
# SKILLS TEST: DELETE ROUTE — Removes a record by auto-increment id
# WARNING: This uses GET method (clicking a link deletes the record).
# For better security, change to POST method with a form button.
# This is a HARD delete (permanent). For soft delete, add is_deleted column.
# ============================================================================
@app.route("/delete/<int:id>")
def delete(id):
    dbhelper.delete_student(id)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # SKILLS TEST: Change port if exam requires: app.run(debug=True, port=8080)
    app.run(debug=True)