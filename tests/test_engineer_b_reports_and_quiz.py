import unittest
from campusflow.reports import generate_ticket_report
from campusflow.understanding_check import evaluate_answer, calculate_score, QUESTIONS
from campusflow.notes import add_note, get_ticket_notes


class TestEngineerBReportsAndQuiz(unittest.TestCase):
    """Authored by Engineer B: Reports, notes lifecycle, understanding check, and bug-hunter tests."""

    def setUp(self):
        self.fixtures = {
            "T001": {
                "id": "T001",
                "title": "Wi-Fi outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": "Gabriel",
                "notes": [],
            },
            "T002": {
                "id": "T002",
                "title": "Projector HDMI cable broken",
                "category": "Hardware",
                "urgency": "medium",
                "affected_users": 8,
                "priority": "medium",
                "status": "in_progress",
                "assigned_to": "Kingsley",
                "notes": [],
            },
            "T003": {
                "id": "T003",
                "title": "SPSS license expired",
                "category": "Software",
                "urgency": "low",
                "affected_users": 2,
                "priority": "low",
                "status": "resolved",
                "assigned_to": "Isaac",
                "notes": [],
            },
        }

    def test_scenario10_empty_report_returns_zero_percent_without_crash(self):
        """Scenario 10: Report on empty dataset displays 0.0% without ZeroDivisionError."""
        report = generate_ticket_report({})
        self.assertIn("0.0%", report)
        self.assertIn("Total Tickets               All Active & Closed      0", report)

    def test_scenario11_report_counts_and_resolution_percentage(self):
        """Scenario 11: Report calculates category breakdowns, unresolved vs resolved, and resolution %."""
        report = generate_ticket_report(self.fixtures)
        # Total = 3, Resolved = 1 -> 33.3%
        self.assertIn("33.3%", report)
        self.assertIn("Unresolved Active           Open + In Progress       2", report)
        self.assertIn("Resolved Completed          Closed Lifecycle         1", report)
        self.assertIn("Network                  1", report)
        self.assertIn("Hardware                 1", report)
        self.assertIn("Software                 1", report)

    def test_scenario05_valid_note_added_and_id_sequential(self):
        """Scenario 05: Valid note added to open ticket generates N001, then N002."""
        t = self.fixtures["T001"]
        n1 = add_note(t, "Mentor A", "Rebooted router in hall")
        self.assertIsInstance(n1, dict)
        self.assertEqual(n1["note_id"], "N001")

        n2 = add_note(t, "Mentor B", "Checking switch port lights")
        self.assertIsInstance(n2, dict)
        self.assertEqual(n2["note_id"], "N002")
        self.assertEqual(len(get_ticket_notes(t)), 2)

    def test_scenario06_invalid_note_rejected_without_consuming_id(self):
        """Scenario 06: Blank author or short message (<5 chars) rejected without consuming note ID."""
        t = self.fixtures["T001"]
        # Blank author raises ValueError
        with self.assertRaises(ValueError):
            add_note(t, "   ", "Valid message here")

        # Too short message raises ValueError
        with self.assertRaises(ValueError):
            add_note(t, "Mentor A", "abc")

        # Valid note added next must still receive N001 (not N003)
        n1 = add_note(t, "Mentor A", "Valid message after failure")
        self.assertIsInstance(n1, dict)
        self.assertEqual(n1["note_id"], "N001")

    def test_scenario07_resolved_ticket_rejects_notes_until_reopened(self):
        """Scenario 07: Resolved ticket rejects new notes; reopen enables notes again."""
        t = self.fixtures["T003"]  # resolved
        with self.assertRaises(ValueError):
            add_note(t, "Mentor A", "Trying to add note on resolved ticket")

        # Reopen ticket to open
        t["status"] = "open"
        res_accept = add_note(t, "Mentor A", "Note after explicit reopen succeeds")
        self.assertIsInstance(res_accept, dict)
        self.assertEqual(res_accept["note_id"], "N001")

    def test_scenario14_understanding_check_scoring_and_evaluation(self):
        """Scenario 14: Understanding check evaluates correct answers and calculates accurate score."""
        correct_answers = {q["id"]: q["correct"] for q in QUESTIONS}
        self.assertEqual(calculate_score(correct_answers), 6)

        # Mix of correct and incorrect
        partial_answers = {
            1: "B",  # Correct
            2: "A",  # Wrong (Crash)
            3: "B",  # Correct
            4: "A",  # Wrong
            5: "C",  # Correct
            6: "B",  # Correct
        }
        self.assertEqual(calculate_score(partial_answers), 4)

    def test_bug_hunter_for_engineer_a_mutation_invariance(self):
        """Bug-Hunter Test for Engineer A: Invalid operations must leave ticket state 100% unchanged."""
        target_ticket = {
            "id": "T099",
            "title": "Core fiber line cut",
            "category": "Network",
            "urgency": "high",
            "affected_users": 100,
            "priority": "critical",
            "status": "resolved",
            "assigned_to": "Gabriel",
            "notes": [{"note_id": "N001", "author": "Gabriel", "message": "Repaired splicing"}],
        }
        import copy
        snapshot = copy.deepcopy(target_ticket)

        # Attempt invalid note addition on resolved ticket raises ValueError
        with self.assertRaises(ValueError):
            add_note(target_ticket, "Intruder", "Illegal note injection")

        # Invariant check: the ticket must remain byte-for-byte identical to its snapshot
        self.assertEqual(target_ticket, snapshot)
        self.assertEqual(len(target_ticket["notes"]), 1)


if __name__ == "__main__":
    unittest.main()
