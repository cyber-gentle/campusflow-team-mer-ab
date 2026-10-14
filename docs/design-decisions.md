# CampusFlow — Architecture & Design Decisions

## 1. Team Roles & Responsibilities

* **Engineer A (cyber-gentle / Abraham David)**:
  * Core ticket creation and validation logic (`campusflow/tickets.py`).
  * Automated priority calculation engine implementing Rules 1–4.
  * JSON storage layer and error boundaries (`campusflow/storage.py`).
  * Matching unit test suite for tickets and persistence (`tests/test_tickets.py`, `tests/test_storage.py`).

* **Engineer B (nnamanimerit94 / Merit Nnamani)**:
  * Helpdesk CLI workflow and role-based menu navigation (`campusflow/workflow.py`).
  * Lifecycle management (`open` → `in_progress` → `resolved` with explicit reopen guards).
  * Priority-based work queue with numeric ID tie-breaking.
  * Reporting engine (`campusflow/reports.py`) and matching tests (`tests/test_workflow.py`).

---

## 2. Agreed Function Contracts & Data Structures

### Ticket Schema
All tickets are stored in a dictionary keyed by their unique formatted ID (`"T001"`, `"T002"`...):
```json
{
  "id": "T001",
  "title": "Campus Wi-Fi is down",
  "category": "Network",
  "urgency": "high",
  "affected_users": 15,
  "priority": "critical",
  "status": "open",
  "assigned_to": null
}
```

* **Valid Categories**: `Network`, `Hardware`, `Software`, `Other`.
* **Valid Urgencies**: `low`, `medium`, `high`.
* **Valid Statuses**: `open`, `in_progress`, `resolved`.

### Priority Calculation Contract
Checked strictly in priority order:
1. `urgency == "high" and affected_users >= 10` &rarr; `"critical"`
2. `urgency == "high" or affected_users >= 10` &rarr; `"high"`
3. `urgency == "medium" or affected_users >= 3` &rarr; `"medium"`
4. All remaining valid tickets &rarr; `"low"`

Implemented using Python pattern matching (`match / case`) with guard clauses.

### Signaling Invalid Input
* Core functions (`create_ticket`, `load_tickets`, `save_tickets`) return string error messages when arguments fail validation rather than crashing the process.
* The CLI layer displays the clear error message to the user and re-prompts or safely continues the menu loop.

### Persistence Ownership
* `campusflow/storage.py` is the single source of truth for file I/O (`data/tickets_logs.json`).
* If file is missing or empty, it initializes a clean in-memory dictionary.
* If file contains malformed JSON, it returns an explicit error message and refuses to silently overwrite damaged data.
* ID generation inspects all existing keys in storage to calculate `max(id) + 1`, guaranteeing strictly unique IDs across app restarts.

---

## 3. Testability Decisions
* Pure business logic (`calculate_priority`, `create_ticket`, `load_tickets`, `save_tickets`, `generate_ticket_report`) takes explicit arguments and returns deterministic dictionaries/tuples.
* Workflow interactive methods read from `sys.stdin`, enabling comprehensive, isolated automated tests via `io.StringIO` mocks without manual typing.
