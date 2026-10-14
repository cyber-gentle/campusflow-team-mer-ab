import unittest
from campusflow.search import filter_tickets, sort_tickets_by_priority


class TestSearchAndFiltering(unittest.TestCase):
    """Authored by Engineer B: Multi-filter search engine and sorting tests."""

    def setUp(self):
        self.fixtures = {
            "T001": {
                "id": "T001",
                "title": "Campus Wi-Fi dropping in science hall",
                "category": "Network",
                "priority": "critical",
                "status": "open",
                "assigned_to": "Gabriel",
            },
            "T002": {
                "id": "T002",
                "title": "Dorm WI-FI router needs reboot",
                "category": "Network",
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "Kingsley",
            },
            "T003": {
                "id": "T003",
                "title": "Lab PC blue screen crash",
                "category": "Hardware",
                "priority": "high",
                "status": "open",
                "assigned_to": None,
            },
            "T004": {
                "id": "T004",
                "title": "Python compiler wifi library error",
                "category": "Software",
                "priority": "low",
                "status": "resolved",
                "assigned_to": "Isaac",
            },
        }

    def test_search_title_case_insensitive_substring(self):
        """Scenario 08: Title search matches case-insensitively ('WI-FI' matches 'Wi-Fi' and 'wifi')."""
        matches_upper = filter_tickets(self.fixtures, title="WI-FI")
        matches_lower = filter_tickets(self.fixtures, title="wifi")

        # T001, T002, T004 have wifi/Wi-Fi in title
        ids_upper = {t["id"] for t in matches_upper}
        ids_lower = {t["id"] for t in matches_lower}

        self.assertIn("T001", ids_upper)
        self.assertIn("T002", ids_upper)
        self.assertIn("T004", ids_upper)
        self.assertEqual(ids_upper, ids_lower)

    def test_combined_filters_use_logical_and(self):
        """Scenario 09: Combined filters for title, category, and status use strict logical AND."""
        # Search for title='wifi' AND category='Network' AND status='open'
        results = filter_tickets(
            self.fixtures,
            title="wifi",
            category="Network",
            status="open",
        )
        # Only T001 matches all three criteria simultaneously
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "T001")

    def test_empty_filters_skipped(self):
        """Empty or whitespace filter strings are skipped and do not restrict matches."""
        results = filter_tickets(
            self.fixtures,
            title="",
            category="Hardware",
            status="   ",
            priority="",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "T003")

    def test_search_read_only_semantics(self):
        """Search operations must not modify ticket dictionary contents."""
        before_state = {k: v.copy() for k, v in self.fixtures.items()}
        _ = filter_tickets(self.fixtures, title="wifi", category="Network")
        self.assertEqual(self.fixtures, before_state)

    def test_sort_search_results_by_priority_and_numeric_id_tie(self):
        """Search results sort critical > high > medium > low, breaking ties by earlier numeric ID."""
        matches = [self.fixtures["T002"], self.fixtures["T001"], self.fixtures["T003"]]
        sorted_matches = sort_tickets_by_priority(matches)

        # Both T001 and T002 are critical; T001 must appear first
        self.assertEqual(sorted_matches[0]["id"], "T001")
        self.assertEqual(sorted_matches[1]["id"], "T002")
        self.assertEqual(sorted_matches[2]["id"], "T003")


if __name__ == "__main__":
    unittest.main()
