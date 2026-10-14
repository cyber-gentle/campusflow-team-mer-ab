# CampusFlow — CLI Helpdesk Management System

CampusFlow is a robust, Python-based Command-Line Helpdesk Ticket Management System designed to record, prioritize, assign, and track technical support requests across a campus environment.

---

## 1. Team Members & Contributions

* **Abraham David (@cyber-gentle)**:
  * **Role**: Engineer A
  * **Contributions**: Core ticket creation and validation logic, automated priority calculation engine, JSON storage layer with error handling, and unit test suites (`tests/test_tickets.py`, `tests/test_storage.py`).
  * **PR**: [#7 feat/3-ticket-creation](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/7)

* **Merit Nnamani (@nnamanimerit94)**:
  * **Role**: Engineer B
  * **Contributions**: Interactive menu system, role-based access, ticket assignment, status lifecycle transitions, work queue with numeric tie-breaking, reporting summary, and workflow tests (`tests/test_workflow.py`).
  * **PR**: [#10 feat/6-tickets-reports](https://github.com/cyber-gentle/campusflow-team-mer-ab/pull/10)

---

## 2. Requirements & Setup

* **Python Version**: Python 3.10+ (requires structural pattern matching support)
* **Dependencies**: Standard Python Library only (`json`, `unittest`, `io`, `sys`, `os`). No third-party frameworks required.

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

CampusFlow provides role-based access for `administrator` and `standard_user`:

| Option | Action | Description | Access |
| :---: | :--- | :--- | :---: |
| **1** | **Create Ticket** | Prompts for title, category, urgency, and affected users. Generates unique ID (`T001`...) | All Users |
| **2** | **List All Tickets** | Displays a clean tabular overview of all logged tickets | All Users |
| **3** | **View Ticket Details** | Displays all metadata fields for a specific ticket ID | All Users |
| **4** | **Assign Ticket** | Assigns or reassigns an open ticket to a staff member | Admin Only |
| **5** | **Update Ticket Status**| Advances lifecycle (`open` &rarr; `in_progress` &rarr; `resolved`) or reopens | All Users |
| **6** | **View Work Queue** | Shows unresolved tickets ordered by priority, breaking ties by earlier numeric ID | Admin Only |
| **7** | **Generate Reports** | Displays total ticket count and breakdowns by status and priority | Admin Only |
| **8** | **Exit** | Saves state and safely exits the program | All Users |

---

## 4. Business Rules

### Priority Calculation Engine
Calculated strictly in order, applying the first match:
1. **Critical**: `urgency == "high"` AND `affected_users >= 10`
2. **High**: `urgency == "high"` OR `affected_users >= 10`
3. **Medium**: `urgency == "medium"` OR `affected_users >= 3`
4. **Low**: All remaining valid tickets

### Status Lifecycle Rules
* **`open` &rarr; `in_progress`**: Allowed **only** if the ticket is assigned to a staff member.
* **`in_progress` &rarr; `resolved`**: Moves the ticket into the resolved state.
* **`resolved` &rarr; `open`**: A resolved ticket cannot be silently modified; it requires an **explicit reopen confirmation** to return to `open`.

---

## 5. Persistence & Storage

* Tickets are stored as structured JSON in `data/tickets_logs.json`.
* **Missing or empty file**: CampusFlow starts with a fresh dictionary automatically.
* **Corrupted JSON**: The persistence layer displays an explicit error message and refuses to silently overwrite damaged data.
* **Starting Fresh**: Delete or clear `data/tickets_logs.json` to start with a blank database.

---

## 6. Running Automated Tests

Run the full automated test suite using Python's standard `unittest` test discovery:

```bash
python3 -m unittest discover -s tests -v
```

### Test Coverage Highlights
* **Priority Engine**: Evaluates boundary cases for all 4 rules (e.g. high+12 &rarr; critical, high+2 &rarr; high, low+4 &rarr; medium, low+1 &rarr; low).
* **Validation**: Rejection of blank titles, zero or negative affected users, invalid categories, and invalid urgencies.
* **Lifecycle & Guards**: Asserts that unassigned tickets cannot enter `in_progress`, and tests explicit reopen behavior.
* **Work Queue Sorting**: Verifies priority sorting and tie-breaking by earlier numeric ticket ID.
* **Persistence**: Asserts round-trip persistence, non-duplication of IDs after reloading, and protection against malformed JSON.

---

## 7. Known Limitations & Future Improvements

1. **Authentication**: Roles (`administrator` vs `standard_user`) are selected at runtime without password authentication.
2. **Dynamic Staff Roster**: Staff mentors are currently configured in a defined list; future releases can add a dynamic staff management module.
3. **Concurrency**: Designed for single-instance CLI operations; multi-user concurrent writes would benefit from file locking.
