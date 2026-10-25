# ============================================================================
# SKILLS TEST QUESTIONNAIRE: NATIONAL VOTING SYSTEM (main.py)
# ============================================================================
# EXAM SCENARIO:
#   Automated multi-position digital voting platform with seat quota enforcement,
#   voter authentication, anti-duplicate voting, and real-time tabulation.
#
# CANDIDATE TASKS & OBJECTIVES (WHAT NEEDS TO BE DONE):
# 1. POSITION MANAGEMENT (/positions):
#    - Define positions with seat counts (posSeats >= 1).
# 2. CANDIDATE MANAGEMENT (/candidates):
#    - Associate candidates with positions, implement soft deactivation.
# 3. VOTER AUTHENTICATION (/login, /logout):
#    - Verify voterID and password, store session["voterID"].
# 4. DIGITAL BALLOT (/vote):
#    - Validate that voter has not previously voted (hasVoted == 0).
#    - Validate that candidate selections per position do NOT exceed posSeats.
#    - Atomic transaction: insert votes into Votes, set hasVoted = 1 on Voters.
# 5. TABULATION & WINNERS (/results, /winners):
#    - Calculate vote counts and percentage of votes per position.
#    - Rank and proclaim top N candidates where N = posSeats.
# ============================================================================

import os

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

import dbhelper

app = Flask(__name__)
# SKILLS TEST: Change this secret key to match your exam requirements
app.secret_key = "philippine-national-election-local"


# SKILLS TEST: Context processor — makes person_name() available in ALL templates
# Useful for displaying full names (first + middle + last) in HTML
@app.context_processor
def inject_helpers():
    return {"person_name": dbhelper.person_name}


# SKILLS TEST: Helper to check that required text fields are not empty
def require_text(*values):
    return all(value.strip() for value in values)


# SKILLS TEST: Helper to validate integer fields with minimum value
# Change the minimum (currently 1) if exam requires different validation
def read_seats(raw):
    try:
        seats = int(raw)
    except (TypeError, ValueError):
        return None
    if seats < 1:
        return None
    return seats


# SKILLS TEST: Helper to validate status field
# Change ("active", "inactive") to your exam's allowed status values
def read_status(raw):
    if raw in ("active", "inactive"):
        return raw
    return None


# ============================================================================
# SKILLS TEST: HOME ROUTE — Dashboard with record counts
# Shows summary statistics. Change if exam wants a different landing page.
# ============================================================================
@app.route("/")
def home():
    # SKILLS TEST: The DB file must exist before the app can run
    # It's created manually with: sqlite3.exe Election.db ".read schema.sql"
    if not os.path.exists(dbhelper.DB_NAME):
        abort(500, "Election.db is missing. Create it with sqlite3.exe and schema.sql.")
    return render_template("index.html", counts=dbhelper.get_counts())


# ============================================================================
# SKILLS TEST: POSITIONS CRUD — List / Add / Edit / Deactivate
# This is a MULTI-PAGE pattern: separate pages for list, add, edit.
# Copy this pattern for any new entity the exam requires.
# ============================================================================
@app.route("/positions")
def positions():
    return render_template("positions.html", positions=dbhelper.get_positions())


# SKILLS TEST: ADD POSITION — GET shows form, POST processes form
# Pattern: validate → call dbhelper → flash message → redirect
@app.route("/positions/add", methods=["GET", "POST"])
def add_position():
    if request.method == "POST":
        # SKILLS TEST: Change form field names to match your HTML form
        pos_name = request.form.get("posName", "").strip()
        seats = read_seats(request.form.get("numOfPositions", "").strip())
        pos_stat = read_status(request.form.get("posStat"))
        if not pos_name:
            flash("Position name is required.", "error")
        elif seats is None:
            flash("Number of seats must be a whole number of at least 1.", "error")
        elif pos_stat is None:
            flash("Select a valid status.", "error")
        else:
            dbhelper.add_position(pos_name, seats, pos_stat)
            flash("Position added.", "success")
            return redirect(url_for("positions"))
    # SKILLS TEST: position=None signals the template to show an empty (add) form
    return render_template("position_form.html", position=None)


# SKILLS TEST: EDIT POSITION — loads existing record, then updates on POST
@app.route("/positions/edit/<int:pos_id>", methods=["GET", "POST"])
def edit_position(pos_id):
    position = dbhelper.get_position(pos_id)
    if position is None:
        abort(404)
    if request.method == "POST":
        pos_name = request.form.get("posName", "").strip()
        seats = read_seats(request.form.get("numOfPositions", "").strip())
        pos_stat = read_status(request.form.get("posStat"))
        if not pos_name:
            flash("Position name is required.", "error")
        elif seats is None:
            flash("Number of seats must be a whole number of at least 1.", "error")
        elif pos_stat is None:
            flash("Select a valid status.", "error")
        else:
            dbhelper.update_position(pos_id, pos_name, seats, pos_stat)
            flash("Position updated.", "success")
            return redirect(url_for("positions"))
    # SKILLS TEST: position=existing_record pre-fills the form for editing
    return render_template("position_form.html", position=position)


# SKILLS TEST: DEACTIVATE (soft delete) — sets status to 'inactive' instead of DELETE
# This is safer than hard delete since it preserves data integrity.
# If exam requires hard delete, use DELETE FROM instead.
@app.route("/positions/deactivate/<int:pos_id>", methods=["POST"])
def deactivate_position(pos_id):
    if dbhelper.get_position(pos_id) is None:
        abort(404)
    dbhelper.deactivate_position(pos_id)
    flash("Position deactivated.", "success")
    return redirect(url_for("positions"))


# ============================================================================
# SKILLS TEST: CANDIDATES CRUD — Same pattern as Positions
# Candidates have a FOREIGN KEY to Positions (posID).
# ============================================================================
@app.route("/candidates")
def candidates():
    return render_template("candidates.html", candidates=dbhelper.get_candidates())


# SKILLS TEST: ADD CANDIDATE — includes a dropdown for selecting position (FK)
@app.route("/candidates/add", methods=["GET", "POST"])
def add_candidate():
    # SKILLS TEST: Load positions for the dropdown select in the form
    positions = dbhelper.get_positions()
    if request.method == "POST":
        # SKILLS TEST: Change field names to match exam columns
        first = request.form.get("candFName", "").strip()
        middle = request.form.get("candMName", "").strip()
        last = request.form.get("candLName", "").strip()
        cand_stat = read_status(request.form.get("candStat"))
        try:
            pos_id = int(request.form.get("posID", ""))
        except ValueError:
            pos_id = None
        if not require_text(first, last):
            flash("First name and last name are required.", "error")
        elif pos_id is None or cand_stat is None:
            flash("Select a position and a valid status.", "error")
        else:
            try:
                dbhelper.add_candidate(first, middle, last, pos_id, cand_stat)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                flash("Candidate added.", "success")
                return redirect(url_for("candidates"))
    return render_template("candidate_form.html", candidate=None, positions=positions)


# SKILLS TEST: EDIT CANDIDATE — same pattern, loads existing + positions dropdown
@app.route("/candidates/edit/<int:cand_id>", methods=["GET", "POST"])
def edit_candidate(cand_id):
    candidate = dbhelper.get_candidate(cand_id)
    if candidate is None:
        abort(404)
    positions = dbhelper.get_positions()
    if request.method == "POST":
        first = request.form.get("candFName", "").strip()
        middle = request.form.get("candMName", "").strip()
        last = request.form.get("candLName", "").strip()
        cand_stat = read_status(request.form.get("candStat"))
        try:
            pos_id = int(request.form.get("posID", ""))
        except ValueError:
            pos_id = None
        if not require_text(first, last):
            flash("First name and last name are required.", "error")
        elif pos_id is None or cand_stat is None:
            flash("Select a position and a valid status.", "error")
        else:
            try:
                dbhelper.update_candidate(cand_id, first, middle, last, pos_id, cand_stat)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                flash("Candidate updated.", "success")
                return redirect(url_for("candidates"))
    return render_template(
        "candidate_form.html",
        candidate=candidate,
        positions=positions,
    )


@app.route("/candidates/deactivate/<int:cand_id>", methods=["POST"])
def deactivate_candidate(cand_id):
    if dbhelper.get_candidate(cand_id) is None:
        abort(404)
    dbhelper.deactivate_candidate(cand_id)
    flash("Candidate deactivated.", "success")
    return redirect(url_for("candidates"))


# ============================================================================
# SKILLS TEST: VOTERS CRUD — Same CRUD pattern as above
# Voters have a TEXT primary key (voterID) instead of INTEGER.
# Voters also have a password field (voterPass) for authentication.
# ============================================================================
@app.route("/voters")
def voters():
    return render_template("voters.html", voters=dbhelper.get_voters())


# SKILLS TEST: ADD VOTER — includes voterID (manual text PK) and password
@app.route("/voters/add", methods=["GET", "POST"])
def add_voter():
    if request.method == "POST":
        voter_id = request.form.get("voterID", "").strip()
        voter_pass = request.form.get("voterPass", "")
        first = request.form.get("voterFName", "").strip()
        middle = request.form.get("voterMName", "").strip()
        last = request.form.get("voterLName", "").strip()
        voter_stat = read_status(request.form.get("voterStat"))
        if not voter_id or not voter_pass or not require_text(first, last):
            flash("Voter ID, password, first name, and last name are required.", "error")
        elif voter_stat is None:
            flash("Select a valid status.", "error")
        else:
            try:
                dbhelper.add_voter(voter_id, voter_pass, first, middle, last, voter_stat)
            except ValueError as exc:
                flash(str(exc), "error")
            else:
                flash("Voter added.", "success")
                return redirect(url_for("voters"))
    return render_template("voter_form.html", voter=None)


@app.route("/voters/edit/<voter_id>", methods=["GET", "POST"])
def edit_voter(voter_id):
    voter = dbhelper.get_voter(voter_id)
    if voter is None:
        abort(404)
    if request.method == "POST":
        voter_pass = request.form.get("voterPass", "")
        first = request.form.get("voterFName", "").strip()
        middle = request.form.get("voterMName", "").strip()
        last = request.form.get("voterLName", "").strip()
        voter_stat = read_status(request.form.get("voterStat"))
        if not voter_pass or not require_text(first, last):
            flash("Password, first name, and last name are required.", "error")
        elif voter_stat is None:
            flash("Select a valid status.", "error")
        else:
            dbhelper.update_voter(voter_id, voter_pass, first, middle, last, voter_stat)
            flash("Voter updated.", "success")
            return redirect(url_for("voters"))
    return render_template("voter_form.html", voter=voter)


@app.route("/voters/deactivate/<voter_id>", methods=["POST"])
def deactivate_voter(voter_id):
    if dbhelper.get_voter(voter_id) is None:
        abort(404)
    dbhelper.deactivate_voter(voter_id)
    flash("Voter deactivated.", "success")
    return redirect(url_for("voters"))


# ============================================================================
# SKILLS TEST: LOGIN / AUTHENTICATION
# Uses Flask session to store logged-in voter's ID and name.
# Pattern: POST with credentials → authenticate() → store in session → redirect
# SKILLS TEST: Change session keys and field names if exam requires.
# ============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        voter_id = request.form.get("voterID", "").strip()
        voter_pass = request.form.get("voterPass", "")
        # SKILLS TEST: authenticate() checks ID + password in the database
        voter = dbhelper.authenticate(voter_id, voter_pass)
        if voter is None:
            flash("Invalid voter ID or password.", "error")
        elif voter["voterStat"] != "active":
            flash("Your account is inactive. You cannot vote.", "error")
        else:
            # SKILLS TEST: Store user info in session for later use
            # session["voterID"] is used to check if user is logged in
            session["voterID"] = voter["voterID"]
            session["voterName"] = dbhelper.person_name(
                voter["voterFName"], voter["voterMName"], voter["voterLName"]
            )
            return redirect(url_for("vote"))
    return render_template("login.html")


# SKILLS TEST: LOGOUT — clears session and redirects to login
@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("login"))


# ============================================================================
# SKILLS TEST: VOTING PAGE — The most complex route
# Builds a ballot (positions + candidates per position), validates selections,
# enforces seat limits, prevents double voting, then records votes.
# SKILLS TEST: This is the KEY BUSINESS LOGIC to understand and adapt.
# ============================================================================
@app.route("/vote", methods=["GET", "POST"])
def vote():
    # SKILLS TEST: Check if user is logged in via session
    voter_id = session.get("voterID")
    if not voter_id:
        return redirect(url_for("login"))
    voter = dbhelper.get_voter(voter_id)
    if voter is None:
        session.clear()
        return redirect(url_for("login"))

    # SKILLS TEST: Check if voter is blocked (inactive or already voted)
    blocked = None
    if voter["voterStat"] != "active":
        blocked = "inactive"
    elif voter["voted"] == "y":
        blocked = "voted"

    # SKILLS TEST: get_ballot() returns positions + their active candidates
    ballot = [] if blocked else dbhelper.get_ballot()
    if request.method == "POST":
        if blocked == "inactive":
            flash("Your account is inactive. You cannot vote.", "error")
            return redirect(url_for("vote"))
        if blocked == "voted":
            flash("You have already voted.", "error")
            return redirect(url_for("vote"))
        # SKILLS TEST: Collect selections — form fields named "choice_{posID}"
        # Each position can have multiple selections (checkboxes)
        selections = []
        for item in ballot:
            position = item["position"]
            for cand_id in request.form.getlist(f"choice_{position['posID']}"):
                try:
                    selections.append((position["posID"], int(cand_id)))
                except ValueError:
                    flash("The ballot contained an invalid choice.", "error")
                    return render_template(
                        "vote.html",
                        voter=voter,
                        ballot=ballot,
                        blocked=None,
                        selected=request.form,
                    )
        try:
            # SKILLS TEST: cast_votes() validates & inserts all votes atomically
            dbhelper.cast_votes(voter["voterID"], selections)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template(
                "vote.html",
                voter=voter,
                ballot=ballot,
                blocked=None,
                selected=request.form,
            )
        flash("Your ballot has been recorded. You cannot vote again.", "success")
        return redirect(url_for("vote"))

    return render_template(
        "vote.html",
        voter=voter,
        ballot=ballot,
        blocked=blocked,
        selected=None,
    )


# ============================================================================
# SKILLS TEST: RESULTS & WINNERS — Read-only report pages
# results: shows vote counts and percentages per candidate per position
# winners: shows the top N candidates per position (N = numOfPositions)
# ============================================================================
@app.route("/results")
def results():
    return render_template("results.html", results=dbhelper.get_results())


@app.route("/winners")
def winners():
    return render_template("winners.html", winners=dbhelper.get_winners())


if __name__ == "__main__":
    # SKILLS TEST: The DB must be created first using:
    #   sqlite3.exe Election.db ".read schema.sql"
    if not os.path.exists(dbhelper.DB_NAME):
        raise SystemExit("Election.db is missing. Create it with sqlite3.exe and schema.sql.")
    # SKILLS TEST: Change port if exam requires: app.run(debug=True, port=8080)
    app.run(debug=True)

