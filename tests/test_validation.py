"""
Unit tests for centralized validation helpers and lifecycle invariants (Engineer A).
Covers: AC-A1, AC-A2, AC-A3, and Bug-Hunter test.
"""

import unittest
from campusflow.validation import (
    can_transition,
    validate_assignment,
    validate_ticket_data,
    validate_ticket_id,
)
from campusflow.tickets import create_ticket


class TestTicketValidationAndInvariants(unittest.TestCase):

    def setUp(self):
        self.open_unassigned = {
            "id": "T001",
            "title": "Core Switch Port Flapping",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": [],
        }

        self.resolved_ticket = {
            "id": "T002",
            "title": "Lab Projector Replacement",
            "category": "Hardware",
            "urgency": "medium",
            "affected_users": 5,
            "priority": "medium",
            "status": "resolved",
            "assigned_to": "Gabriel",
            "notes": [],
        }

    def test_ac_a1_unassigned_open_ticket_cannot_transition_to_in_progress(self):
        """AC-A1: Unassigned open ticket attempting transition to in_progress is rejected; ticket remains open and unchanged."""
        allowed, reason = can_transition(self.open_unassigned, "in_progress")
        self.assertFalse(allowed)
        self.assertIn("must be assigned", reason.lower())
        # Assert ticket remained completely unchanged
        self.assertEqual(self.open_unassigned["status"], "open")
        self.assertIsNone(self.open_unassigned["assigned_to"])

    def test_ac_a2_invalid_affected_users_returns_error_dict(self):
        """AC-A2: Invalid affected_users (0, -5, 4.2, True, 'five') returns error dict."""
        invalid_cases = [0, -5, 4.2, True, False, "five", None, [10]]
        for val in invalid_cases:
            with self.subTest(val=val):
                res = validate_ticket_data("Valid Title", "Network", "high", val)
                self.assertIsInstance(res, dict)
                self.assertFalse(res.get("success", True))
                self.assertIn("positive integer", res.get("error", "").lower())

    def test_ac_a2_create_ticket_returns_error_dict_on_invalid_affected_users(self):
        """AC-A2: create_ticket does not halt on error, but returns error details dict."""
        tickets = {}
        res = create_ticket(tickets, "Server down", "Network", "high", True, raise_on_error=True)
        self.assertEqual(res, {"error": "Affected users must be a positive integer.", "success": False})
        self.assertEqual(len(tickets), 0, "Collection must remain empty on validation failure")

    def test_ac_a3_resolved_ticket_assignment_mutation_rejected(self):
        """AC-A3: Resolved ticket assignment or reassignment is rejected until explicitly reopened."""
        allowed, reason = validate_assignment(self.resolved_ticket, "Isaac")
        self.assertFalse(allowed)
        self.assertIn("cannot assign or reassign a resolved ticket", reason.lower())
        # Assert assignment remained untouched
        self.assertEqual(self.resolved_ticket["assigned_to"], "Gabriel")

    def test_category_normalization_and_whitelist(self):
        """Category is normalized to canonical title-case or returns error dict if invalid."""
        for raw, expected in [("network", "Network"), ("  hardware  ", "Hardware"), ("SOFTWARE", "Software"), ("other", "Other")]:
            with self.subTest(raw=raw):
                res = validate_ticket_data("Valid Title", raw, "low", 1)
                self.assertTrue(res.get("success"))
                self.assertEqual(res.get("category"), expected)

        res_err = validate_ticket_data("Valid Title", "Billing", "low", 1)
        self.assertFalse(res_err.get("success", True))
        self.assertIn("category", res_err.get("error", "").lower())

    def test_urgency_normalization_and_whitelist(self):
        """Urgency is normalized to lowercase or returns error dict if invalid."""
        for raw, expected in [("HIGH", "high"), ("  Medium ", "medium"), ("low", "low")]:
            with self.subTest(raw=raw):
                res = validate_ticket_data("Valid Title", "Network", raw, 1)
                self.assertTrue(res.get("success"))
                self.assertEqual(res.get("urgency"), expected)

        res_err = validate_ticket_data("Valid Title", "Network", "emergency", 1)
        self.assertFalse(res_err.get("success", True))
        self.assertIn("urgency", res_err.get("error", "").lower())

    def test_validate_title_rejects_blank_strings(self):
        """Blank or whitespace-only title returns error dict."""
        for blank_title in ["   ", "", None, 123]:
            with self.subTest(title=blank_title):
                res = validate_ticket_data(blank_title, "Network", "low", 1)
                self.assertFalse(res.get("success", True))
                self.assertIn("title", res.get("error", "").lower())

    def test_bug_hunter_failed_validation_leaves_ticket_collection_untouched(self):
        """
        Bug-Hunter Test (Engineer A):
        Ensures validate-before-mutate invariant: an attempt to create an invalid ticket
        never leaves a partial entry or dirty state in the tickets dictionary.
        """
        tickets = {
            "T001": {
                "id": "T001",
                "title": "Valid Ticket",
                "category": "Network",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        }
        original_keys = list(tickets.keys())

        # Attempt to create with invalid boolean affected_users
        res = create_ticket(tickets, "Crashing attempt", "Network", "high", True)
        self.assertIsInstance(res, dict)
        self.assertFalse(res["success"])
        self.assertIn("positive integer", res["error"])

        # Invariant check: collection size and keys are identical
        self.assertEqual(list(tickets.keys()), original_keys)
        self.assertNotIn("T002", tickets)

    def test_validate_ticket_id(self):
        """Validates ticket ID format with re.fullmatch(r'T\\d{3,}')."""
        valid_ids = ["T001", "T042", "T999", "T1000", "T123456", "  T001  "]
        for tid in valid_ids:
            with self.subTest(tid=tid):
                self.assertTrue(validate_ticket_id(tid))

        invalid_ids = ["T", "T1", "T02", "T12", "123", "T001a", "T001-fix", "T12T34", "", None, 123, []]
        for tid in invalid_ids:
            with self.subTest(tid=tid):
                self.assertFalse(validate_ticket_id(tid))


if __name__ == "__main__":
    unittest.main()

