# PRACTICAL SKILLS TEST QUESTIONNAIRE: SYSTEM 02
## Bookstore Inventory & Valuation System

---

### EXAM METADATA
- **Examination Code:** `SKILL-TEST-2026-BOOK-02`
- **Course / Module:** Web Systems Development & Action-Dispatched CRUD Applications
- **Allowed Time:** 2 Hours
- **Total Points:** 100 Points
- **Tech Stack:** Python 3.x, Flask, SQLite3, Jinja2, HTML5 / CSS3

---

## 1. Scenario & Problem Statement
The *University Bookstore & Publications Office* needs a streamlined, single-screen desktop inventory terminal to track published books by their unique ISBN, maintain retail prices and stock quantities, and calculate real-time inventory valuations.

Unlike standard multi-page applications, **this system operates on a single unified console (`index.html`) using POST action dispatching** (Search, Add, Update, Delete), displaying the active book record in the top form while rendering the full inventory and valuation summary below.

As the examinee, **you must implement and verify the entire action-dispatched workflow** and inventory value aggregation.

---

## 2. System Architecture & Directory Layout

```text
NEW/Bookssyste,/
├── main.py         # Flask app with unified action-dispatched controller route
├── dbhelper.py     # SQLite helper with CRUD, seed loader, and valuation math
├── books.db        # SQLite database file (auto-generated)
└── templates/
    └── index.html  # Single-page terminal UI with Action buttons and Inventory Table
```

---

## 3. Database Specification & Data Dictionary

Database filename: `books.db`

### Table: `books`
| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `isbn` | INTEGER | PRIMARY KEY | Unique ISBN / Product Code (e.g. `1001`) |
| `title` | TEXT | NOT NULL | Title of the publication |
| `copyright` | TEXT | NOT NULL | Copyright year (e.g. `2024`) |
| `edition` | TEXT | NOT NULL | Edition name/number (e.g. `1st`, `2nd`) |
| `price` | REAL | NOT NULL | Unit retail price |
| `quantity` | INTEGER | NOT NULL | Quantity in stock |

---

## 4. Skills Test Tasks: "What Needs To Be Done"

### Part 1: Database Operations in `dbhelper.py` (30 Points)
- [ ] **Task 1.1 — Schema Definition (`create_table()`):**
  Create table `books` with `isbn` as the primary key.
- [ ] **Task 1.2 — Seed Data Initialization (`seed_data()`):**
  Check if `books` is empty. If empty, insert at least 4 default books into the database.
- [ ] **Task 1.3 — Fetch All with Calculated Totals (`get_all()`):**
  Fetch all books, calculate each book's total valuation (`price * quantity`), compute the grand inventory total:
  $$\text{Grand Total} = \sum_{i=1}^{n} (\text{price}_i \times \text{quantity}_i)$$
  Return a tuple `(rows_with_totals, grand_total)`.
- [ ] **Task 1.4 — Lookup (`get_book(isbn)`):**
  Retrieve a single book by `isbn` returning a dictionary or `None`.
- [ ] **Task 1.5 — Insert (`add_book(...)`):**
  Insert a new book record.
- [ ] **Task 1.6 — Update (`update_book(...)`):**
  Update `title`, `copyright`, `edition`, `price`, and `quantity` for an existing `isbn`.
- [ ] **Task 1.7 — Delete (`delete_book(isbn)`):**
  Delete the book corresponding to the given `isbn`.

### Part 2: Controller & Action Dispatching in `main.py` (40 Points)
- [ ] **Task 2.1 — Action Dispatch Router (`/`):**
  Accept both `GET` and `POST`. Read the hidden field `action = request.form.get("action")`.
- [ ] **Task 2.2 — Action: `search`:**
  Look up book by `isbn`. If found, set `message = "ITEM FOUND"` and populate form fields; if not found, set `message = "ITEM NOT FOUND"`.
- [ ] **Task 2.3 — Action: `add`:**
  Read form inputs, call `dbhelper.add_book()`, set `message = "RECORD ADDED"`.
- [ ] **Task 2.4 — Action: `update`:**
  Update record, set `message = "RECORD UPDATED"`.
- [ ] **Task 2.5 — Action: `delete`:**
  Delete record by `isbn`, set `message = "RECORD DELETED"`.
- [ ] **Task 2.6 — Inventory Table Data:**
  In all cases, fetch latest records and total via `dbhelper.get_all()` to render in the table.

### Part 3: UI & Jinja Templating in `index.html` (20 Points)
- [ ] **Task 3.1 — Action Buttons:**
  Provide distinct submit buttons sending `action="search"`, `action="add"`, `action="update"`, `action="delete"`.
- [ ] **Task 3.2 — Form Pre-Population:**
  When a book is found, pre-fill form fields with `{{ book['title'] }}`, `{{ book['price'] }}`, etc.
- [ ] **Task 3.3 — Status Message:**
  Display status feedback message at top of form.
- [ ] **Task 3.4 — Inventory Table:**
  Render columns: ISBN, Title, Copyright, Edition, Price, Quantity, Total. Display Grand Total at table bottom.

### Part 4: Data Validation & Code Quality (10 Points)
- [ ] **Task 4.1 — Type Casting:** Cast `isbn` and `quantity` to `int`, and `price` to `float`.
- [ ] **Task 4.2 — SQL Injection Prevention:** Use parameterized queries (`?`) for all operations.

---

## 5. Grading Rubric (100 Points Total)

| Section | Criteria | Points |
|---|---|---|
| **Database Operations** | Schema setup, seed data, queries, valuation formula | 30 pts |
| **Action Dispatching** | Correct handling of search, add, update, delete actions | 40 pts |
| **Template & State UI** | Single-page UI, form state persistence, table rendering | 20 pts |
| **Code Quality & Integrity** | Parameterized queries, connection cleanup, type safety | 10 pts |
| **TOTAL** | **Comprehensive Practical Score** | **100 pts** |

---

## 6. How to Run & Verify

1. **Start the Flask Application:**
   ```bash
   python main.py
   ```
2. **Access the Console:**
   Open browser to `http://127.0.0.1:5000/`
3. **Verification Steps:**
   - **Search:** Enter `1001` and click Search. Verify title and price populate form.
   - **Add:** Enter new ISBN `1005`, Title "Flask Web Development", Price `450.00`, Qty `10`. Click Add.
   - **Valuation Check:** Verify the table displays new row with total `4,500.00` and updated grand total.
   - **Update:** Search `1005`, modify quantity to `15`, click Update. Total changes to `6,750.00`.
   - **Delete:** Enter `1005` and click Delete. Record removed from table.
