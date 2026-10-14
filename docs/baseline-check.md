# CampusFlow — Baseline Diagnostic & Regression Check

**Date:** 2026-10-14  
**Engineer:** Engineer A (Wealth Ibe)  
**Branch:** `feat/21-validation-and-notes`  
**Audited Commit:** `10a8827` (HEAD of `main`)  

---

## 1. Test Suite Baseline Execution

* **Command:** `python3 -m unittest discover -s tests -v`
* **Result:** `22 passed, 0 failed, 0 errors` in `0.018s`
* **Output Summary:**
  * `test_storage`: 5 tests passed (load/save, missing file, empty file, malformed JSON, reload ID continuity).
  * `test_tickets`: 10 tests passed (rules 1–4, boundary cases, input rejections for empty title, invalid category/urgency, positive integer affected users).
  * `test_workflow`: 7 tests passed (unassigned transition rejection, status progression, explicit reopen prompt, work queue priority/tie-break ordering, report outputs).

---

## 2. Interactive & Functional Inputs Tested

### Input Test 1: Assignment on a Resolved Ticket
* **Action:** Attempting to assign or reassign a staff member to a ticket currently in `status: "resolved"` (e.g. `T008`).
* **Observed Behavior:** `TicketManager.assign_tickets()` does not inspect `ticket["status"]`. It allows staff assignment on a resolved ticket without requiring the ticket to be reopened.
* **Audit Finding Confirmed:** **Yes.** Violates the invariant: *"A resolved ticket cannot accept new notes or assignment modifications unless it is explicitly reopened first."*

### Input Test 2: Presence of Follow-up Notes Field in Data
* **Action:** Inspecting loaded tickets in `data/tickets_logs.json` for the `'notes'` field (`ticket.get('notes')`).
* **Observed Behavior:** All existing 12 tickets in `data/tickets_logs.json` lack the `'notes'` key. Attempting to access `ticket['notes']` raises a `KeyError`, and no `notes.py` module exists yet.
* **Audit Finding Confirmed:** **Yes.** New requirement requires ticket schema extension with `'notes': []` and per-ticket note IDs (`N001`, `N002`, ...).

### Input Test 3: Structural Validation on JSON Load
* **Action:** Calling `load_tickets()` on a file containing invalid record structures (e.g. missing keys, invalid category, or status mismatch).
* **Observed Behavior:** `load_tickets()` in `campusflow/storage.py` only validates that `json.loads()` succeeds. It performs no structural, key, or invariant validation on the loaded dictionary before returning it to the caller.
* **Audit Finding Confirmed:** **Yes.** Violates the invariant: *"Parse and validate the entire JSON collection before replacing in-memory tickets."*

---

## 3. Scope of Improvements for Sprint (Issue #21)

1. **Centralized Validation ([campusflow/validation.py](file:///home/sntino/campusflow-team-mer-ab/campusflow/validation.py)):**
   * Guard `affected_users` to strictly reject booleans (`isinstance(True, int)` is True), floats, strings, and non-positive numbers with `ValueError`.
   * Enforce category normalization to canonical whitelist (`Network`, `Hardware`, `Software`, `Other`).
   * Enforce status lifecycle invariants: block unassigned tickets moving to `in_progress`, block modifications to `resolved` tickets without reopening.
   * Ensure validate-before-mutate guarantees.

2. **Follow-Up Notes Engine ([campusflow/notes.py](file:///home/sntino/campusflow-team-mer-ab/campusflow/notes.py)):**
   * Extend ticket schema with `'notes': []`.
   * Implement `add_note(ticket, author, message) -> dict` and `next_note_id(ticket) -> str`.
   * Enforce 5–300 character message length, non-blank author, rejection on resolved tickets, and ensure failed attempts never consume note IDs.

3. **Defensive Storage & Migration ([campusflow/storage.py](file:///home/sntino/campusflow-team-mer-ab/campusflow/storage.py)):**
   * Validate entire dataset before in-memory state replacement.
   * Guarantee ID continuity for tickets and notes.
   * Migrate existing tickets in `data/tickets_logs.json` to safely include `'notes': []`.
