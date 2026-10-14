"""
Unit tests for centralized validation helpers and lifecycle invariants (Engineer A).
Covers: AC-A1, AC-A2, AC-A3, and Bug-Hunter test.
"""

import unittest
from campusflow.validation import (
    can_transition,
    normalize_category,
    normalize_urgency,
    validate_affected_users,
    validate_assignment,
    validate_ticket_data,
    validate_title,
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

    def test_ac_a2_invalid_affected_users_rejected_with_value_error(self):
        """AC-A2: Invalid affected_users (0, -5, 4.2, True, 'five') is rejected with ValueError."""
        invalid_cases = [0, -5, 4.2, True, False, "five", None, [10]]
        for val in invalid_cases:
            with self.subTest(val=val):
                with self.assertRaises(ValueError):
                    validate_affected_users(val)

    def test_ac_a2_create_ticket_raises_on_invalid_affected_users_when_requested(self):
        """AC-A2: create_ticket raises ValueError when raise_on_error=True for invalid affected_users."""
        tickets = {}
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Server down", "Network", "high", True, raise_on_error=True)
        self.assertEqual(len(tickets), 0, "Collection must remain empty on validation failure")

    def test_ac_a3_resolved_ticket_assignment_mutation_rejected(self):
        """AC-A3: Resolved ticket assignment or reassignment is rejected until explicitly reopened."""
        allowed, reason = validate_assignment(self.resolved_ticket, "Isaac")
        self.assertFalse(allowed)
        self.assertIn("cannot assign or reassign a resolved ticket", reason.lower())
        # Assert assignment remained untouched
        self.assertEqual(self.resolved_ticket["assigned_to"], "Gabriel")

    def test_category_normalization_and_whitelist(self):
        """Category is normalized to canonical title-case or rejected if invalid."""
        self.assertEqual(normalize_category("network"), "Network")
        self.assertEqual(normalize_category("  hardware  "), "Hardware")
        self.assertEqual(normalize_category("SOFTWARE"), "Software")
        self.assertEqual(normalize_category("other"), "Other")

        with self.assertRaises(ValueError):
            normalize_category("Billing")

    def test_urgency_normalization_and_whitelist(self):
        """Urgency is normalized to lowercase or rejected if invalid."""
        self.assertEqual(normalize_urgency("HIGH"), "high")
        self.assertEqual(normalize_urgency("  Medium "), "medium")
        self.assertEqual(normalize_urgency("low"), "low")

        with self.assertRaises(ValueError):
            normalize_urgency("emergency")

    def test_validate_title_rejects_blank_strings(self):
        """Blank or whitespace-only title raises ValueError."""
        with self.assertRaises(ValueError):
            validate_title("   ")
        with self.assertRaises(ValueError):
            validate_title("")

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
        self.assertIsInstance(res, str)
        self.assertIn("positive integer", res)

        # Invariant check: collection size and keys are identical
        self.assertEqual(list(tickets.keys()), original_keys)
        self.assertNotIn("T002", tickets)


if __name__ == "__main__":
    unittest.main()
