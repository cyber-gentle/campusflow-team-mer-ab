# [FEAT] Issue #21: Ticket Validation, Follow-Up Notes Engine & Safe JSON Persistence

## 🎯 Overview & Context
* **Assignee**: Engineer A (Abraham David — Ticket Safety & Storage Engineer)
* **Target Branch**: `feat/21-validation-and-notes`
* **Parent Milestone**: CampusFlow Next — Progression Sprint (Reliability & Quality)
* **GitHub Issues URL**: https://github.com/cyber-gentle/campusflow-team-mer-ab/issues/new

CampusFlow requires enterprise-grade reliability: ticket state invariants must be guaranteed before mutations, notes must follow a strict lifecycle, and persistent JSON storage must parse and validate the entire dataset before modifying in-memory state.

---

## 📋 User Story
As a campus support engineer, I need CampusFlow to:
1. Prevent invalid ticket creation, illegal status changes, and unauthorized mutations of resolved tickets.
2. Support structured follow-up notes on active tickets with deterministic note IDs (`N001`, `N002`, ...).
3. Safely persist and reload tickets and notes from disk without corrupting memory or generating colliding IDs.

---

## 🛠️ Scope of Work & Technical Contracts

### 1. Centralized Validation Helpers & Lifecycle Guards
Implement in a dedicated validation module (or `campusflow/tickets.py`):
- **Category Normalization & Whitelist**: Must match `Network`, `Hardware`, `Software`, or `Other`.
- **Urgency**: Must be one of `low`, `medium`, or `high`.
- **Affected Users**: Must be a strictly positive integer (`affected_users > 0`). Explicitly reject floats (`1.5`), strings (`"10"`), and booleans (`True`/`False`, noting `isinstance(True, int) is True` in Python).
- **Title**: Non-empty string after trimming whitespace.
- **Assignment Guard**: An unassigned `open` ticket (`assigned_to is None` or `""`) **must never** transition to `in_progress`.
- **State Mutation Safety**: Mutation attempts on invalid inputs must leave the existing ticket collection 100% untouched.
- **Resolved Ticket Protection**: A `resolved` ticket cannot accept new notes or assignment modifications unless it is explicitly reopened first.

### 2. Structured Follow-up Notes Engine
Expose in `campusflow/notes.py`:
- **Ticket Schema Extension**: Extend tickets with `'notes': []`.
- **Note Schema**: `{'note_id': 'N001', 'author': str, 'message': str}`.
- **API Function Contract**:
  ```python
  def add_note(ticket: dict, author: str, message: str) -> dict:
      """
      Validates and appends a follow-up note to an open or in_progress ticket.
      Raises ValueError if ticket is resolved, author is blank, 
      or message length is not within 5 to 300 characters after trimming.
      Rejected attempts must not consume a note ID.
      """
  ```
- **Note ID Continuity**: Auto-generate per-ticket IDs (`next_note_id(ticket)`) starting at `N001`.

### 3. Defensive JSON Persistence & ID Continuity
Update `campusflow/storage.py`:
- **Validate Before Replacing**: Parse and validate the entire JSON collection before replacing in-memory tickets.
- **Strict Validation Rules on Load**:
  - Valid structure (dict of tickets or list).
  - All required keys present (`id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`, `notes`).
  - No duplicate ticket IDs.
  - Consistency between urgency/affected users and priority.
  - Valid status and note shapes.
- **State Preservation on Failure**: If any record is malformed or invalid, reject the load, raise/return a descriptive error, and preserve current in-memory tickets without data loss.
- **ID Continuity**: Ensure `next_ticket_id()` and `next_note_id()` correctly inspect loaded records so new IDs never collide.

---

## 🧪 Acceptance Criteria & Automated Tests

Author at least **5 automated unit tests** (in `tests/test_validation.py` and `tests/test_storage.py`):
- [ ] **AC-A1**: Unassigned open ticket attempting transition to `in_progress` is rejected; ticket remains `open` and unchanged.
- [ ] **AC-A2**: Invalid `affected_users` (`0`, `-5`, `4.2`, `True`, `"five"`) is rejected with `ValueError`.
- [ ] **AC-A3**: Resolved ticket assignment or note mutation is rejected.
- [ ] **AC-A4**: Valid note added receives correct sequential ID (`N001`), and blank/too-short notes (<5 chars) are rejected without consuming an ID.
- [ ] **AC-A5**: Note on resolved ticket rejected; note accepted after reopen.
- [ ] **AC-A6**: Malformed JSON or JSON with duplicate IDs is rejected with state completely preserved.
- [ ] **AC-A7**: Reloading tickets properly continues next ticket ID and note IDs.

---

## 🔒 Definition of Done
1. Code follows pure Python standard library conventions (no external dependencies).
2. All 5+ automated tests pass with `python3 -m unittest discover -s tests -v`.
3. AI Learning Log updated in `docs/ai-learning-log.md` with at least 2 learning cycles (including 1 rejected/modified AI suggestion).
4. Pull Request opened against `main` targeting Issue #21 with clear review instructions for Engineer B.
