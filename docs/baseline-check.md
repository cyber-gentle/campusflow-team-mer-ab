# CampusFlow — Baseline Diagnostic & Regression Check

**Date:** 2026-10-14  
**Sprint:** CampusFlow Next — Progression Sprint  
**Audited Commit:** `10a8827` / `d9bf9ba`  
**Engineer Roles:**
* **Engineer A (Wealth Ibe):** Ticket Safety, State Mutation Invariants & Safe Storage (`feat/7-validation-and-notes`)
* **Engineer B (Merit Nnamani):** Search, Reports, CLI Notes UI & Understanding Check (`feat/9-search-and-insights`)

---

## 1. Test Suite Baseline Execution

* **Command:** `python3 -m unittest discover -s tests -v`
* **Result:** `22 passed, 0 failed, 0 errors` in `0.026s`
* **Output Summary:**
  * `test_storage`: 5 tests passed (load/save, missing file, empty file, malformed JSON, reload ID continuity).
  * `test_tickets`: 10 tests passed (rules 1–4, boundary cases, input rejections for empty title, invalid category/urgency, positive integer affected users).
  * `test_workflow`: 7 tests passed (unassigned transition rejection, status progression, explicit reopen prompt, work queue priority/tie-break ordering, report outputs).

---

## 2. Interactive & Functional Inputs Tested

### Engineer A Baseline Inputs
1. **Assignment on a Resolved Ticket:**
   * **Action:** Attempting to assign or reassign a staff member to a ticket currently in `status: "resolved"` (e.g. `T008`).
   * **Observed Behavior:** `TicketManager.assign_tickets()` does not inspect `ticket["status"]`. It allowed staff assignment on a resolved ticket without requiring reopen.
   * **Audit Finding Confirmed:** **Yes.** Violates invariant: *"A resolved ticket cannot accept new notes or assignment modifications unless it is explicitly reopened first."*

2. **Presence of Follow-up Notes Field in Data:**
   * **Action:** Inspecting loaded tickets in `data/tickets_logs.json` for the `'notes'` field (`ticket.get('notes')`).
   * **Observed Behavior:** Baseline tickets lacked the `'notes'` key, risking `KeyError`.
   * **Audit Finding Confirmed:** **Yes.** Required schema extension with `'notes': []` and sequential note IDs (`N001`, `N002`, ...).

3. **Structural Validation on JSON Load:**
   * **Action:** Calling `load_tickets()` on a file containing malformed or duplicate-ID records.
   * **Observed Behavior:** Baseline only verified `json.loads()` succeeded, without structural/schema validation before returning to caller.
   * **Audit Finding Confirmed:** **Yes.** Violates invariant: *"Parse and validate the entire JSON collection before replacing in-memory tickets."*

### Engineer B Baseline Inputs
1. **Ticket Creation & Priority Calculation:**
   * **Input:** Title: `"Lab switch port dead"`, Category: `Network`, Urgency: `high`, Affected users: `15`.
   * **Observed Result:** Ticket created with ID `T001` and priority `critical` (Rule 1 match).

2. **Unassigned Ticket Status Transition Guard:**
   * **Input:** Attempt to advance unassigned ticket `T001` from `open` to `in_progress`.
   * **Observed Result:** Transition rejected with message `"Ticket must be assigned before it can move to in-progress"`. State preserved as `open`.

3. **Work Queue Ordering & Tie-Breaking:**
   * **Input:** Active tickets with identical priority (`critical` for `T002` and `T003`).
   * **Observed Result:** `T002` ordered before `T003` (tie broken by earlier numeric ticket ID).

---

## 3. Scope of Improvements for Sprint

| Area | Current Baseline | CampusFlow Next Requirement | Owner |
| :--- | :--- | :--- | :--- |
| **Validation & Invariants** | Basic `affected_users` check | Reject booleans (`isinstance(True, int)`), floats, strings; normalize category to whitelist | Engineer A |
| **Lifecycle Safety** | Basic check | Disallow unassigned open → in_progress; freeze resolved tickets from assignment/notes | Engineer A |
| **Notes Storage Engine** | None | Schema extension with `'notes': []`, `add_note()`, `next_note_id()`, reject resolved notes | Engineer A |
| **Defensive JSON Storage** | `json.loads` check only | Validate full collection before replacing memory; reject corrupt/duplicate-ID files | Engineer A |
| **Search Engine** | None (only view single ID) | Multi-filter search (case-insensitive substring title + category + status + priority via logical AND) | Engineer B |
| **Trustworthy Reports** | Basic count / status | Add category counts, unresolved count, resolved count, and resolution % (safe from zero-division) | Engineer B |
| **Notes CLI Interface** | None | Add Option 8 (Add Note) and Option 9 (View Notes) with validation & friendly error feedback | Engineer B |
| **Understanding Check** | None | Interactive 6-question CLI Understanding Check with validation and score tracking | Engineer B |
