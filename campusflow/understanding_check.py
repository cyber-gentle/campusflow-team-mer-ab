"""Interactive CLI Engineering Understanding Check for CampusFlow Next (Engineer B).

Separates question data bank from scoring evaluation logic and interactive CLI loop.
Validates input choices (A/B/C/D) with non-terminating retry loops.
"""

QUESTIONS = [
    {
        "id": 1,
        "question": "Ticket T001 is open and unassigned. A user tries to move it to in_progress. What should happen?",
        "options": {
            "A": "Accept the change and proceed",
            "B": "Reject and preserve all data unchanged",
            "C": "Resolve it automatically",
            "D": "Remove the ticket from the system",
        },
        "correct": "B",
        "explanation": "State invariant: a ticket must be assigned before entering in_progress. Rejected mutations must not alter data.",
    },
    {
        "id": 2,
        "question": "The application has zero tickets logged. What should the resolution percentage display?",
        "options": {
            "A": "Crash with ZeroDivisionError",
            "B": "100%",
            "C": "0%",
            "D": "Divide by 1 without explanation",
        },
        "correct": "C",
        "explanation": "Guarded arithmetic: when total tickets count is 0, resolution rate must safely evaluate to 0.0% without crashing.",
    },
    {
        "id": 3,
        "question": "Filter title='wifi', category='Network', status='open'. Which records should match?",
        "options": {
            "A": "Any record matching at least one filter (logical OR)",
            "B": "Only records matching all supplied filters (logical AND)",
            "C": "All Network records regardless of title or status",
            "D": "All open records",
        },
        "correct": "B",
        "explanation": "Search filter composition requires logical AND across all non-empty supplied filter fields.",
    },
    {
        "id": 4,
        "question": "A ticket currently marked 'resolved' receives a request to 'Add note'. What should happen?",
        "options": {
            "A": "Append the note anyway",
            "B": "Delete old notes and replace with new note",
            "C": "Reject until explicitly reopened through valid workflow",
            "D": "Change status to open silently without asking",
        },
        "correct": "C",
        "explanation": "Resolved tickets are frozen from mutations including new notes and assignment until explicitly reopened.",
    },
    {
        "id": 5,
        "question": "The JSON file on disk includes two tickets with the same ID. What should load_tickets do?",
        "options": {
            "A": "Keep both tickets in memory",
            "B": "Replace memory with the duplicate tickets",
            "C": "Reject the load without changing current memory",
            "D": "Rename the duplicate IDs silently",
        },
        "correct": "C",
        "explanation": "Data integrity: corrupted or duplicate-ID JSON must be rejected to prevent corrupting the valid in-memory collection.",
    },
    {
        "id": 6,
        "question": "A PR changes input validation logic but contains no negative-case tests. What is the best review action?",
        "options": {
            "A": "Approve because the code syntax looks clean",
            "B": "Request focused negative-case tests and reasoning before merging",
            "C": "Merge immediately to keep velocity high",
            "D": "Ask an external AI to approve the PR",
        },
        "correct": "B",
        "explanation": "Engineering rigor: peer review requires verifying that invalid inputs are explicitly rejected with negative tests.",
    },
]


def get_question_bank() -> list[dict]:
    """Return immutable copy of the understanding check question bank."""
    return [q.copy() for q in QUESTIONS]


def evaluate_answer(question_id: int, user_choice: str) -> bool:
    """Evaluate whether user choice matches the correct answer for a question."""
    normalized_choice = str(user_choice).strip().upper()
    for q in QUESTIONS:
        if q["id"] == question_id:
            return normalized_choice == q["correct"]
    return False


def calculate_score(answers: dict[int, str]) -> int:
    """Calculate total score (0 to 6) based on submitted answers."""
    score = 0
    for q in QUESTIONS:
        if evaluate_answer(q["id"], answers.get(q["id"], "")):
            score += 1
    return score


def run_understanding_check() -> int:
    """Execute the interactive Engineering Understanding Check CLI session.
    
    Prompts all 6 questions, validates input, requests explanations for
    two selected questions, and prints the final score.
    """
    print("""
=======================================================================
               CAMPUSFLOW ENGINEERING UNDERSTANDING CHECK              
=======================================================================
Answer each scenario question by entering A, B, C, or D.
""")
    answers: dict[int, str] = {}

    for q in QUESTIONS:
        print(f"\nQ{q['id']}. {q['question']}")
        for opt_key in ("A", "B", "C", "D"):
            print(f"   [{opt_key}] {q['options'][opt_key]}")

        while True:
            choice = input("Your answer (A/B/C/D): ").strip().upper()
            if choice in ("A", "B", "C", "D"):
                answers[q["id"]] = choice
                break
            print("Invalid input! Please enter only A, B, C, or D.")

    score = calculate_score(answers)

    # Prompt user for at least two explanations as required by Section 05
    print("\n-----------------------------------------------------------------------")
    print("Self-Explanation Check: Explain the reasoning for two questions.")
    print("-----------------------------------------------------------------------")
    for q_id in (1, 3):
        exp = input(f"Briefly explain your answer to Question {q_id}: ").strip()
        while not exp:
            exp = input(f"Please provide a short explanation for Question {q_id}: ").strip()

    print(f"""
=======================================================================
                         QUIZ RESULTS SUMMARY                          
=======================================================================
Final Score: {score} / {len(QUESTIONS)} points ({score / len(QUESTIONS) * 100:.1f}%)
""")
    for q in QUESTIONS:
        user_ans = answers.get(q["id"], "-")
        is_correct = "CORRECT" if user_ans == q["correct"] else "INCORRECT"
        print(f"Q{q['id']}: [{user_ans}] -> {is_correct} (Correct: [{q['correct']}])")
        print(f"     Reason: {q['explanation']}")
    print("=======================================================================\n")

    return score
