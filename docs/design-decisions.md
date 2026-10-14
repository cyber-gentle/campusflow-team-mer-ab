# CampusFlow — Architecture & Design Decisions

## 1. Team Roles & Responsibilities

* **Engineer A (cyber-gentle / Wealth Ibe / Abraham David)**:
  * Centralized validation helpers & lifecycle invariants (`campusflow/validation.py`).
  * Core ticket creation and validation logic (`campusflow/tickets.py`).
  * Automated priority calculation engine implementing Rules 1–4.
  * Structured follow-up notes data layer & ID sequencing (`campusflow/notes.py`).
  * Defensive JSON persistence, schema validation, and atomic writes (`campusflow/storage.py`).
  * Matching unit test suite (`tests/test_validation.py`, `tests/test_notes.py`, `tests/test_storage.py`).

* **Engineer B (nnamanimerit94 / Merit Nnamani)**:
  * Helpdesk CLI workflow and role-based menu navigation (`campusflow/workflow.py`).
  * Lifecycle management (`open` → `in_progress` → `resolved` with explicit reopen guards).
  * Priority-based work queue with numeric ID tie-breaking.
  * Multi-filter search engine and reporting analytics (`campusflow/reports.py`).
  * Interactive Engineering Understanding Check and workflow tests (`tests/test_workflow.py`).

---

## 2. Agreed Function Contracts & Data Structures

### Ticket Schema (Extended for CampusFlow Next)
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
  "assigned_to": null,
  "notes": [
    {
      "note_id": "N001",
      "author": "Kingsley",
      "message": "Rebooted core distribution switch in Admin building."
    }
  ]
}
```

* **Valid Categories**: `Network`, `Hardware`, `Software`, `Other` (normalized to canonical title-case).
* **Valid Urgencies**: `low`, `medium`, `high` (normalized to lowercase).
* **Valid Statuses**: `open`, `in_progress`, `resolved`.
* **Note Structure**: `{"note_id": str, "author": str, "message": str}`.

### Validation Invariants & Rules
1. **Strict Type Safety for Affected Users**:
   * Must be a positive integer (`affected_users >= 1`).
   * Explicitly disallows booleans (`isinstance(True, int)` is `True` in Python, so checked via `isinstance(x, int) and not isinstance(x, bool)`), floats, strings, or negative integers. Raises `ValueError`.
2. **Assignment Invariant**:
   * An unassigned `open` ticket (`assigned_to is None` or `""`) cannot move to `in_progress`.
   * A `resolved` ticket cannot accept staff assignment or reassignment unless explicitly reopened first.
3. **Validate-Before-Mutate**:
   * If any argument is invalid, the operation immediately raises an exception or returns an error, guaranteeing the in-memory ticket collection is 100% unchanged.

### Follow-Up Notes Contract (`campusflow/notes.py`)
```python
def add_note(ticket: dict, author: str, message: str) -> dict:
    """
    Validates and appends a follow-up note to an open or in_progress ticket.
    Raises ValueError if ticket is resolved, author is blank, 
    or message length is not within 5 to 300 characters after trimming.
    Rejected attempts must not consume a note ID.
    """
```
* **Note ID Continuity**: Per-ticket deterministic sequence (`N001`, `N002`, ...), determined by `next_note_id(ticket)`.
* **State Protection**: Resolved tickets reject new notes until explicitly reopened. Rejected notes never burn an ID.

### Priority Calculation Contract
Checked strictly in priority order:
1. `urgency == "high" and affected_users >= 10` &rarr; `"critical"`
2. `urgency == "high" or affected_users >= 10` &rarr; `"high"`
3. `urgency == "medium" or affected_users >= 3` &rarr; `"medium"`
4. All remaining valid tickets &rarr; `"low"`

### Defensive Persistence & Storage Ownership (`campusflow/storage.py`)
* **Validate Before Overwriting**:
  `load_tickets()` runs deep structural, key, priority, and note schema validation across the entire JSON dataset before replacing memory.
* **Corrupt & Duplicate Protection**:
  If JSON is malformed or contains duplicate/mismatched IDs, the load is rejected and existing in-memory state is protected.
* **Atomic Writes**:
  `save_tickets()` writes to a temporary file via `tempfile.NamedTemporaryFile` in the target directory and replaces atomically using `os.replace()`, preventing zero-byte truncation if interrupted.
* **Backward Compatibility**:
  Legacy files without a `"notes"` key automatically receive `"notes": []` on load and save.

---

## 3. Testability Decisions
* Pure business logic (`calculate_priority`, `validate_ticket_data`, `add_note`, `can_transition`, `validate_ticket_collection`) operates on explicit parameters and returns deterministic results or raises explicit `ValueError`s.
* Invariant tests assert collection state both before and after rejected actions to prove non-mutation.
