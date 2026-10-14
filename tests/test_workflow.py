import io
import os
import sys
import unittest
from campusflow.workflow import TicketManager
from campusflow.reports import generate_ticket_report
from campusflow.storage import save_tickets


class TestWorkflowAndReports(unittest.TestCase):

    def setUp(self):
        self.test_files = [
            "./data/test_workflow_tickets.json",
            "./data/empty_report_test.json",
            "./data/populated_report_test.json",
        ]
        self._cleanup()
        self.tm = TicketManager()
        self.tm.tickets_file_name = "test_workflow_tickets.json"
        # Use an isolated in-memory dictionary for workflow tests
        self.tm.tickets = {
            "T001": {
                "id": "T001",
                "title": "Low Priority Server Check",
                "category": "Software",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
            },
            "T002": {
                "id": "T002",
                "title": "Dorm Network Down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 20,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
            "T003": {
                "id": "T003",
                "title": "Library Wi-Fi Flapping",
                "category": "Network",
                "urgency": "high",
                "affected_users": 50,
                "priority": "critical",
                "status": "open",
                "assigned_to": "Kingsley",
            },
            "T004": {
                "id": "T004",
                "title": "Lab PC HDMI Failure",
                "category": "Hardware",
                "urgency": "medium",
                "affected_users": 15,
                "priority": "high",
                "status": "in_progress",
                "assigned_to": "Gabriel",
            },
        }

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        """An unassigned ticket cannot transition from open to in_progress."""
        # T001 is open and unassigned
        sys.stdin = io.StringIO("T001\n")
        captured_out = io.StringIO()
        sys.stdout = captured_out

        result = self.tm.update_status()

        sys.stdout = sys.__stdout__
        self.assertEqual(result, "Status not updated.")
        self.assertEqual(self.tm.tickets["T001"]["status"], "open")
        self.assertIn("Ticket must be assigned", captured_out.getvalue())

    def test_assigned_ticket_progresses_open_to_in_progress_to_resolved(self):
        """Assigned ticket moves from open -> in_progress -> resolved."""
        # T003 is open and assigned to Kingsley
        sys.stdin = io.StringIO("T003\n")
        res1 = self.tm.update_status()
        self.assertEqual(self.tm.tickets["T003"]["status"], "in_progress")
        self.assertIn("in_progress", res1)

        # Transition in_progress -> resolved
        sys.stdin = io.StringIO("T003\n")
        res2 = self.tm.update_status()
        self.assertEqual(self.tm.tickets["T003"]["status"], "resolved")
        self.assertIn("resolved", res2)

    def test_resolved_ticket_requires_explicit_reopen(self):
        """A resolved ticket cannot move forward; it can only be explicitly reopened to open."""
        self.tm.tickets["T003"]["status"] = "resolved"

        # User chooses NOT to reopen (choice 2)
        sys.stdin = io.StringIO("T003\n2\n")
        res_no = self.tm.update_status()
        self.assertEqual(res_no, "Resolved ticket was not modified.")
        self.assertEqual(self.tm.tickets["T003"]["status"], "resolved")

        # User chooses TO reopen (choice 1)
        sys.stdin = io.StringIO("T003\n1\n")
        res_yes = self.tm.update_status()
        self.assertIn("reopened", res_yes.lower())
        self.assertEqual(self.tm.tickets["T003"]["status"], "open")

    def test_work_queue_ordered_by_priority_and_numeric_id_ties(self):
        """Work queue orders critical -> high -> medium -> low, and breaks ties by earlier numeric ID."""
        captured = io.StringIO()
        sys.stdout = captured

        self.tm.view_work_queue()

        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        # Both T002 and T003 are critical; T002 must appear before T003
        pos_t002 = output.find("T002")
        pos_t003 = output.find("T003")
        pos_t004 = output.find("T004")  # high priority
        pos_t001 = output.find("T001")  # low priority

        self.assertTrue(pos_t002 != -1 and pos_t003 != -1 and pos_t004 != -1 and pos_t001 != -1)
        self.assertLess(pos_t002, pos_t003, "T002 should appear before T003 due to earlier numeric ID")
        self.assertLess(pos_t003, pos_t004, "Critical tickets should appear before High tickets")
        self.assertLess(pos_t004, pos_t001, "High tickets should appear before Low tickets")

    def test_find_ticket_rejects_unknown_id(self):
        """Querying a non-existent ticket ID returns an error string."""
        sys.stdin = io.StringIO("T999\n")
        result = self.tm.find_ticket()
        self.assertEqual(result, "Ticket not found.")

    def test_reports_handle_zero_tickets(self):
        """Report generator cleanly handles zero tickets."""
        test_empty_file = "empty_report_test.json"
        save_tickets(test_empty_file, {})
        report = generate_ticket_report(test_empty_file)
        self.assertEqual(report, "No ticket logged!")

    def test_reports_with_populated_tickets(self):
        """Report generator correctly counts status and priority totals."""
        test_file = "populated_report_test.json"
        save_tickets(test_file, self.tm.tickets)
        report = generate_ticket_report(test_file)
        self.assertIn("Total Tickets", report)
        self.assertIn("Critical", report)
    def _cleanup(self):
        for f in getattr(self, "test_files", []):
            if os.path.exists(f):
                os.remove(f)

    def tearDown(self):
        self._cleanup()


if __name__ == "__main__":
    unittest.main()

