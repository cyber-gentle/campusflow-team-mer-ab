# CampusFlow — AI Learning Log

---

## Fellow: Abraham David (Engineer A)

### Interaction #1 — Python 3.10+ Pattern Matching in State Transitions
* **Problem**: How to refactor complex `if/elif` ladders into clean, readable structural pattern matching without runtime regressions.
* **My initial understanding**: I knew `match/case` existed in Python 3.10+, but wasn't sure how it handles multiple valid values (or-patterns) and guard conditions.
* **Prompt to AI**: "Show a minimal example of Python match-case matching string values with an OR pattern and guard condition. Do not code my project."
* **Useful AI guidance**: AI explained the `case "val1" | "val2":` syntax for alternative values and `case val if condition:` for guards.
* **My independent experiment/test**: Tested `match status: case "in_progress" | "in-progress": return True` in Python terminal.
* **Verification source or result**: Python official `PEP 634` specification and local REPL test output.
* **Decision**: **Accepted and applied** to `campusflow/reports.py` and `campusflow/workflow.py:update_status`.
* **Related file/commit**: `campusflow/reports.py`, `376bf93`
* **What I can now explain without AI**: How to combine `|` patterns and guards to represent clean finite state machines in Python.

### Interaction #2 — Critical AI Evaluation: Alternative Pattern Variable Binding
* **Problem**: Migrating priority calculation with numeric thresholds into pattern matching.
* **My initial understanding**: I expected to combine `("high", _)` and `(_, n)` with an `|` operator in a single case statement.
* **Prompt to AI**: "How can I combine tuple matching with guards in a single line?"
* **Useful AI guidance**: AI suggested `case ("high", _) | (_, n) if n >= 10:`.
* **My independent experiment/test**: Executed the code in `python3 -m unittest discover -s tests -v`. Python raised `SyntaxError: alternative patterns bind different names`.
* **Verification source or result**: Python compiler error: in Python pattern matching, all alternative branches in `|` must bind the exact same variables; one branch binding `n` while the other binds `_` is a compile-time syntax error.
* **Decision**: **Rejected and improved** AI suggestion by separating the rules into distinct `case` arms (`case ("high", _):` and `case (_, n) if n >= 10:`).
* **Related file/commit**: `campusflow/tickets.py:calculate_priority`, `e143bd2`
* **What I can now explain without AI**: The variable binding invariant of PEP 634 alternative patterns and how to structure tuple matching safely.

### Interaction #3 — Differentiating Empty Files from Corrupted JSON
* **Problem**: Ensuring persistence doesn't silently wipe out tickets if JSON is malformed.
* **My initial understanding**: Catching `json.JSONDecodeError` is enough to prevent a program crash.
* **Prompt to AI**: "What is the difference between an empty JSON file and a corrupted JSON file when using json.loads in Python?"
* **Useful AI guidance**: AI demonstrated checking file length (`file.read().strip()`) before calling `json.loads()` so empty files trigger a clean start while non-empty invalid content flags actual corruption.
* **My independent experiment/test**: Created a file containing `{ invalid: content ` and asserted that `load_tickets` returns a clear error message instead of an empty dictionary.
* **Verification source or result**: `tests/test_storage.py:test_malformed_json_produces_clear_error`.
* **Decision**: **Accepted and applied** to `campusflow/storage.py:load_tickets`.
* **Related file/commit**: `campusflow/storage.py`, `tests/test_storage.py`
* **What I can now explain without AI**: How to design defensive I/O boundaries that protect existing persistent data from silent loss.

### Interaction #4 — Strict Integer Type Validation (Rejecting Booleans in Python)
* **Problem**: Preventing boolean values (`True`/`False`) from passing integer validation for `affected_users`.
* **My initial understanding**: I assumed `isinstance(val, int)` was sufficient to validate that `affected_users` is an integer.
* **Prompt to AI**: "Why does isinstance(True, int) return True in Python and how do you ensure an argument is strictly an integer and not a boolean without type checking everything twice?"
* **Useful AI guidance**: AI explained that `bool` is a historical subclass of `int` in Python (`issubclass(bool, int)` is `True`). It suggested using `type(val) is int`.
* **My independent experiment/test**: Tested `type(True) is int` (which is `False`) vs `isinstance(val, int) and not isinstance(val, bool)`. While `type()` works, `isinstance(val, int) and not isinstance(val, bool)` is more explicit and keeps inheritance support if custom int subclasses are ever introduced.
* **Verification source or result**: Verified in REPL and authored `tests/test_validation.py:test_ac_a2_invalid_affected_users_rejected_with_value_error`.
* **Decision**: **Accepted and applied** in `campusflow/validation.py:validate_affected_users`.
* **Related file/commit**: `campusflow/validation.py`, `tests/test_validation.py`
* **What I can now explain without AI**: Why booleans inherit from `int` in Python and how to structure strict scalar type validators.

### Interaction #5 — Critical AI Evaluation: Atomic File Replacement vs Hardcoded Temp Files
* **Problem**: Implementing atomic JSON saves so a process interruption never truncates persistent data.
* **My initial understanding**: Writing directly to `open(file, 'w')` followed by `json.dump()` is how persistence is normally handled.
* **Prompt to AI**: "How can I prevent corrupted JSON files if saving fails halfway in Python standard library?"
* **Useful AI guidance**: AI suggested writing to a fixed temporary file named `file_path + ".tmp"` and then calling `os.rename()`.
* **My independent experiment/test**: Tested `os.rename()` on an existing destination file on Windows/POSIX and considered concurrent access. On Windows, `os.rename()` raises `FileExistsError` if destination exists. Moreover, hardcoding `.tmp` creates collisions in multi-test execution.
* **Verification source or result**: Python official `os.replace` documentation: `os.replace()` is an atomic, cross-platform replacement that overwrites the target file without raising `FileExistsError`.
* **Decision**: **Rejected and improved** AI suggestion by using `tempfile.NamedTemporaryFile(dir=..., delete=False)` combined with `os.replace()`.
* **Related file/commit**: `campusflow/storage.py:save_tickets`.
* **What I can now explain without AI**: The difference between `os.rename` and `os.replace` and how atomic file staging protects databases from partial write corruption.

---

## Fellow: Merit Nnamani (Engineer B)

### Interaction #1 — Non-Interactive CLI Testing with Mocked Stdin
* **Problem**: How to automate testing of CLI prompt functions (`input()`) without hanging the test suite.
* **My initial understanding**: I thought interactive functions could only be tested manually in the terminal.
* **Prompt to AI**: "How can I test functions that use Python's input() using standard library unittest without third party packages?"
* **Useful AI guidance**: AI showed how to patch `sys.stdin = io.StringIO('mock_input\n')` and reset it in `tearDown` or after the function call.
* **My independent experiment/test**: Wrote a test feeding `"T001\n"` into `find_ticket()` and verified the returned dictionary matched without user prompt intervention.
* **Verification source or result**: `tests/test_workflow.py:test_unassigned_ticket_cannot_move_to_in_progress`.
* **Decision**: **Accepted and applied** across `tests/test_workflow.py`.
* **Related file/commit**: `tests/test_workflow.py`
* **What I can now explain without AI**: How Python redirects standard streams using `sys.stdin = io.StringIO(...)` for deterministic automated testing.

### Interaction #2 — Priority Queue Multi-Key Sorting
* **Problem**: How to order tickets by priority first, then break ties using earlier numeric ticket ID.
* **My initial understanding**: Sorting once by priority might leave ties in arbitrary or non-deterministic order.
* **Prompt to AI**: "How does Python sort list of dictionaries by two criteria: a custom rank map, and an extracted integer from a string key?"
* **Useful AI guidance**: AI explained tuple sorting in `list.sort(key=...)`, where Python compares element 0 of the tuple first, then element 1.
* **My independent experiment/test**: Sorted `[('critical', 'T003'), ('critical', 'T001')]` with `key=lambda x: (rank[x[0]], int(x[1][1:]))` and observed `T001` before `T003`.
* **Verification source or result**: `tests/test_workflow.py:test_work_queue_ordered_by_priority_and_numeric_id_ties`.
* **Decision**: **Accepted and applied** to `campusflow/workflow.py:view_work_queue`.
* **Related file/commit**: `campusflow/workflow.py`
* **What I can now explain without AI**: Tuple comparison behavior in Python sorting algorithms and how to break ties reliably.

### Interaction #3 — Reopen Lifecycle State Invariants
* **Problem**: Preventing resolved tickets from being accidentally altered without explicit user reopening.
* **My initial understanding**: Resolved tickets could just automatically transition to closed or open.
* **Prompt to AI**: "What is the recommended design pattern in helpdesk state machines for handling resolved tickets?"
* **Useful AI guidance**: AI suggested requiring an explicit confirmation prompt when a ticket is already in a terminal/resolved state rather than a silent state toggle.
* **My independent experiment/test**: Tested the prompt flow in `update_status()`: choosing `1` reopens to `open`; choosing `2` preserves `resolved` state.
* **Verification source or result**: Verified via `test_resolved_ticket_requires_explicit_reopen`.
* **Decision**: **Accepted and improved** with dedicated user messaging and persistence saving.
* **Related file/commit**: `campusflow/workflow.py:update_status`, `tests/test_workflow.py`
* **What I can now explain without AI**: How to implement guarded state machine transitions that prevent accidental workflow corruption.
