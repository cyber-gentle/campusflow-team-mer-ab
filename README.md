# CampusFlow — CLI Helpdesk Management System

CampusFlow is a robust, Python-based Command-Line Helpdesk Ticket Management System designed to record, prioritize, assign, and track technical support requests across a campus environment.

---

## 1. Team Members & Contributions

* **Abraham David / Wealth Ibe (@cyber-gentle / @wib3)**:
  * **Role**: Engineer A
  * **Initial Sprint**: Core ticket creation and validation logic, automated priority calculation engine, JSON storage layer with error handling, and unit test suites (`tests/test_tickets.py`, `tests/test_storage.py`).
  * **CampusFlow Next Sprint**: Centralized validation & strict scalar type safety (rejecting booleans and floats), structured follow-up notes engine (`campusflow/notes.py`), defensive JSON persistence with whole-collection schema validation, and atomic writes via `os.replace` (`campusflow/storage.py`).
  * **Pull Requests**: [#7 feat/3-ticket-creation](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/7), [#17 feat/21-validation-and-notes](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/17)

* **Merit Nnamani (@nnamanimerit94)**:
  * **Role**: Engineer B
  * **Initial Sprint**: Interactive menu system, role-based access, ticket assignment, status lifecycle transitions, work queue with numeric tie-breaking, reporting summary, and workflow tests (`tests/test_workflow.py`).
  * **CampusFlow Next Sprint**: Multi-filter search engine (`campusflow/search.py`), trustworthy reports with category breakdowns and zero-division safe resolution % (`campusflow/reports.py`), interactive notes CLI interface, and engineering understanding check (`campusflow/understanding_check.py`).
  * **Pull Requests**: [#10 feat/6-tickets-reports](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/10), [#18 feat/22-search-and-insights](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/18)

---

## 2. Requirements & Setup

* **Python Version**: Python 3.10+ (requires structural pattern matching support)
* **Dependencies**: Standard Python Library only (`json`, `unittest`, `io`, `sys`, `os`, `tempfile`). No third-party frameworks required.

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/cyber-gentle/campusflow-team-mer-ab.git
   cd campusflow-team-mer-ab
   ```
2. Run the application:
   ```bash
   python3 main.py
   ```

---

## 3. CLI Menu & Available Options

CampusFlow provides role-based access control for `administrator` and `standard_user`:

| Option | Action | Description | Access |
| :---: | :--- | :--- | :---: |
| **1** | **Create Ticket** | Prompts for title, category, urgency, and affected users. Generates unique ID (`T001`...) | All Users |
| **2** | **List All Tickets** | Displays a clean tabular overview of all logged tickets | All Users |
| **3** | **View Ticket Details** | Displays all metadata fields for a specific ticket ID | All Users |
| **4** | **Assign Ticket** | Assigns or reassigns an open ticket to a staff member (frozen on resolved tickets) | Admin Only |
| **5** | **Update Ticket Status** | Advances lifecycle (`open` &rarr; `in_progress` &rarr; `resolved`) or explicitly reopens | All Users |
| **6** | **View Open Work Queue** | Shows open tickets ordered by priority, breaking ties by earlier numeric ID | Admin Only |
| **7** | **Search Tickets** | Multi-filter search combining title substring, category, status, and priority via logical `AND` | All Users |
| **8** | **Add Follow-up Note** | Appends a structured note (5–300 chars) with auto-sequenced ID (`N001`...) to active tickets | All Users |
| **9** | **View Ticket Notes** | Displays formatted history of all follow-up notes on a ticket | All Users |
| **10** | **Generate Reports** | Displays ticket totals, status/category breakdowns, and zero-division safe resolution % | Admin Only |
| **11** | **Understanding Check** | Interactive 6-question CLI quiz evaluating engineering design patterns and invariants | All Users |
| **12** | **Exit** | Saves state safely and exits the program | All Users |

---

## 4. Business Rules & Invariants

### Priority Calculation Engine
Calculated strictly in order, applying the first matching rule:
1. **Critical**: `urgency == "high"` AND `affected_users >= 10`
2. **High**: `urgency == "high"` OR `affected_users >= 10`
3. **Medium**: `urgency == "medium"` OR `affected_users >= 3`
4. **Low**: All remaining valid tickets

### Status Lifecycle Rules
* **`open` &rarr; `in_progress`**: Allowed **only** if the ticket is assigned to a staff member.
* **`in_progress` &rarr; `resolved`**: Moves the ticket into the resolved state.
* **`resolved` &rarr; `open`**: A resolved ticket cannot be silently modified; it requires an **explicit reopen confirmation** to return to `open`.
* **Resolved State Protection**: Resolved tickets reject new follow-up notes and staff assignment changes until explicitly reopened.

### Validation & Type Safety
* **Strict Scalar Integer Check**: `affected_users` must be a strictly positive integer (`>= 1`). Booleans (`True`/`False`), floats, strings, and non-positive numbers are strictly rejected with `ValueError`.
* **Whitelist Normalization**: Categories are normalized to `Network`, `Hardware`, `Software`, or `Other`. Urgencies are normalized to `low`, `medium`, or `high`.
* **Validate-Before-Mutate**: Operations validate all inputs before modifying collections, guaranteeing zero corrupted or partial state.

### Follow-up Notes Invariants
* Note authors must be non-blank strings.
* Note messages must be between 5 and 300 characters after trimming.
* Per-ticket sequential IDs (`N001`, `N002`, ...) are deterministic.
* Rejected note attempts **never consume** a note ID.

---

## 5. Persistence & Storage Architecture

* Tickets are stored as structured JSON in `data/tickets_logs.json`.
* **Defensive Schema Validation**: `load_tickets()` validates the whole collection before replacing in-memory state. Corrupt files, missing keys, priority mismatches, or duplicate IDs are rejected, preserving in-memory tickets safely.
* **Atomic Writes**: `save_tickets()` writes to a temporary file via `tempfile.NamedTemporaryFile` in the target directory and replaces atomically using `os.replace()`, preventing zero-byte truncation if interrupted.
* **Missing or empty file**: CampusFlow starts with a fresh dictionary automatically.
* **Backward Compatibility**: Legacy ticket files without a `"notes"` key automatically receive `"notes": []` on load and save.

---

## 6. Running Automated Tests

Run the full automated test suite using Python's standard `unittest` test discovery:

```bash
python3 -m unittest discover -s tests -v
```

### Test Coverage Highlights (51 Tests Total)
* **`test_tickets.py` (10 tests)**: Boundary cases for all 4 priority rules, unique sequential ID generation, input validation.
* **`test_storage.py` (6 tests)**: Round-trip persistence, corrupt JSON handling, atomic reload, note & ticket ID continuity post-reload.
* **`test_validation.py` (8 tests)**: Strict integer checks (rejecting booleans), validate-before-mutate invariance, lifecycle guards.
* **`test_notes.py` (8 tests)**: Note length bounds, sequential ID preservation on failures, resolved ticket protection, sorted display.
* **`test_workflow.py` (7 tests)**: Lifecycle guards, work queue priority and tie-breaking, explicit reopen behavior.
* **`test_search.py` (5 tests)**: Case-insensitive substring matching, logical `AND` filter composition, read-only search semantics.
* **`test_engineer_b_reports_and_quiz.py` (7 tests)**: Zero-division handling, understanding check scoring, bug-hunter mutation invariants.

---

## 7. Known Limitations & Future Improvements

1. **Authentication**: Roles (`administrator` vs `standard_user`) are selected at runtime without password authentication.
2. **Dynamic Staff Roster**: Staff mentors are currently configured in a defined list; future releases can add a dynamic staff management module.
3. **Concurrency**: Designed for single-instance CLI operations; multi-user concurrent writes would benefit from file locking.

