# Baseline Diagnostic Check — CampusFlow Next

**Date**: 2026-10-14  
**Audited Commit**: `d9bf9ba`  
**Engineer Roles**: 
* **Engineer A**: Colleague (Ticket Safety, State Mutation Invariants & Safe Storage)
* **Engineer B**: Current Fellow (Search, Reports, CLI Notes UI & Understanding Check)

---

## 1. Test Suite Execution

* **Command**: `python3 -m unittest discover -s tests -v`
* **Result**: `Ran 22 tests in 0.026s — OK`
* **Pass / Fail**: 22 Passed, 0 Failed, 0 Errors.

---

## 2. Baseline Interactive Scenarios Tested

1. **Ticket Creation & Priority Calculation**:
   * **Input**: Title: `"Lab switch port dead"`, Category: `Network`, Urgency: `high`, Affected users: `15`.
   * **Observed Result**: Ticket created with ID `T001` and priority `critical` (Rule 1 match).

2. **Unassigned Ticket Status Transition Guard**:
   * **Input**: Attempt to advance unassigned ticket `T001` from `open` to `in_progress`.
   * **Observed Result**: Transition rejected with message `"Ticket must be assigned before it can move to in-progress"`. State preserved as `open`.

3. **Work Queue Ordering & Tie-Breaking**:
   * **Input**: Active tickets with identical priority (`critical` for `T002` and `T003`).
   * **Observed Result**: `T002` ordered before `T003` (tie broken by earlier numeric ticket ID).

---

## 3. Audit Observations & Scope for CampusFlow Next

| Area | Current Baseline | CampusFlow Next Requirement |
| :--- | :--- | :--- |
| **Search** | None (only list all or view single ticket ID) | Multi-filter search (case-insensitive substring title + category + status + priority using logical AND) |
| **Reports** | Total count, status count, priority count | Add category counts, unresolved count, resolved count, and resolution percentage (safe from division by zero) |
| **Follow-up Notes** | Not supported | Structured notes list (`note_id`, `author`, `message`) per ticket, only on open/in-progress tickets |
| **Knowledge Check**| None | Interactive 6-question CLI Understanding Check with validation and score tracking |
| **Persistence Safety**| Basic empty vs malformed check | Full collection schema validation on load; reject duplicate IDs without corrupting memory |
