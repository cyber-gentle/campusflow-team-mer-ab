import unittest
from campusflow.tickets import calculate_priority, create_ticket


class TestTicketPriorityAndCreation(unittest.TestCase):

    def setUp(self):
        self.tickets = {}

    def test_priority_rule1_high_urgency_and_10_plus_users_is_critical(self):
        """Rule 1: high urgency + 12 affected users -> critical priority."""
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_priority_rule2_high_urgency_or_10_plus_users_is_high(self):
        """Rule 2: high urgency or >= 10 affected users -> high priority."""
        self.assertEqual(calculate_priority("high", 2), "high")
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("medium", 15), "high")

    def test_priority_rule3_medium_urgency_or_3_plus_users_is_medium(self):
        """Rule 3: medium urgency or >= 3 affected users -> medium priority."""
        self.assertEqual(calculate_priority("low", 4), "medium")
        self.assertEqual(calculate_priority("medium", 1), "medium")

    def test_priority_rule4_remaining_is_low(self):
        """Rule 4: all remaining valid tickets -> low priority."""
        self.assertEqual(calculate_priority("low", 1), "low")
        self.assertEqual(calculate_priority("low", 2), "low")

    def test_create_ticket_valid_data(self):
        """Creating a ticket with valid data succeeds and assigns T001."""
        ticket = create_ticket(
            self.tickets,
            title="Wi-Fi is down in science complex",
            category="Network",
            urgency="high",
            affected_users=15
        )
        self.assertIsInstance(ticket, dict)
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIn("T001", self.tickets)

    def test_create_ticket_rejects_zero_or_negative_affected_users(self):
        """Zero or negative affected users are rejected with an error message."""
        result_zero = create_ticket(
            self.tickets,
            title="Broken chair",
            category="Hardware",
            urgency="low",
            affected_users=0
        )
        self.assertEqual(result_zero, "Affected users must be a positive integer.")

        result_neg = create_ticket(
            self.tickets,
            title="Broken chair",
            category="Hardware",
            urgency="low",
            affected_users=-5
        )
        self.assertEqual(result_neg, "Affected users must be a positive integer.")

    def test_create_ticket_rejects_blank_title(self):
        """Blank or whitespace-only title is rejected."""
        result = create_ticket(
            self.tickets,
            title="   ",
            category="Network",
            urgency="high",
            affected_users=5
        )
        self.assertEqual(result, "Title must not be blank.")

    def test_create_ticket_rejects_invalid_category(self):
        """Invalid category not in Network, Hardware, Software, Other is rejected."""
        result = create_ticket(
            self.tickets,
            title="Payment failed",
            category="Finance",
            urgency="medium",
            affected_users=2
        )
        self.assertEqual(result, "Category must be Network, Hardware, Software, or Other.")

    def test_create_ticket_rejects_invalid_urgency(self):
        """Invalid urgency not in low, medium, high is rejected."""
        result = create_ticket(
            self.tickets,
            title="Server down",
            category="Software",
            urgency="urgent",
            affected_users=5
        )
        self.assertEqual(result, "Urgency must be low, medium, or high.")

    def test_incremental_unique_ticket_ids(self):
        """Ticket IDs increment correctly as T001, T002, T003..."""
        t1 = create_ticket(self.tickets, "Issue 1", "Hardware", "low", 1)
        t2 = create_ticket(self.tickets, "Issue 2", "Software", "low", 1)
        t3 = create_ticket(self.tickets, "Issue 3", "Network", "low", 1)
        self.assertEqual(t1["id"], "T001")
        self.assertEqual(t2["id"], "T002")
        self.assertEqual(t3["id"], "T003")


if __name__ == "__main__":
    unittest.main()
