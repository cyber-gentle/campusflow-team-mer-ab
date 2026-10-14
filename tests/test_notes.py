"""
Unit tests for structured follow-up notes engine (Engineer A).
Covers: AC-A4, AC-A5, and note lifecycle invariants.
"""

import unittest
from campusflow.notes import add_note, get_ticket_notes, next_note_id


class TestFollowUpNotesEngine(unittest.TestCase):

    def setUp(self):
        self.open_ticket = {
            "id": "T001",
            "title": "Wi-Fi Access Point Offline",
            "category": "Network",
            "urgency": "high",
            "affected_users": 25,
            "priority": "critical",
            "status": "open",
            "assigned_to": "Kingsley",
            "notes": [],
        }

        self.in_progress_ticket = {
            "id": "T002",
            "title": "Projector Bulb Dead",
            "category": "Hardware",
            "urgency": "medium",
            "affected_users": 30,
            "priority": "medium",
            "status": "in_progress",
            "assigned_to": "Gabriel",
            "notes": [],
        }

        self.resolved_ticket = {
            "id": "T003",
            "title": "Software License Expired",
            "category": "Software",
            "urgency": "low",
            "affected_users": 1,
            "priority": "low",
            "status": "resolved",
            "assigned_to": "Isaac",
            "notes": [],
        }

    def test_ac_a4_valid_note_added_receives_n001(self):
        """AC-A4: Valid note added receives correct sequential ID (N001) and attaches to ticket."""
        note = add_note(self.open_ticket, author="Kingsley", message="Power cycle attempted on router.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Kingsley")
        self.assertEqual(note["message"], "Power cycle attempted on router.")
        self.assertEqual(len(self.open_ticket["notes"]), 1)
        self.assertEqual(self.open_ticket["notes"][0], note)

    def test_ac_a4_sequential_note_ids(self):
        """Sequential notes on the same ticket receive N001, N002, N003."""
        n1 = add_note(self.open_ticket, "Staff A", "First note observation.")
        n2 = add_note(self.open_ticket, "Staff B", "Second note investigation.")
        n3 = add_note(self.open_ticket, "Staff C", "Third note resolution step.")
        self.assertEqual(n1["note_id"], "N001")
        self.assertEqual(n2["note_id"], "N002")
        self.assertEqual(n3["note_id"], "N003")

    def test_ac_a4_blank_author_rejected_without_consuming_id(self):
        """AC-A4: Blank or whitespace-only author is rejected and does not consume a note ID."""
        with self.assertRaises(ValueError):
            add_note(self.open_ticket, author="   ", message="Valid message here.")
        
        # Invariant: notes list is empty and next note ID remains N001
        self.assertEqual(len(self.open_ticket["notes"]), 0)
        self.assertEqual(next_note_id(self.open_ticket), "N001")

    def test_ac_a4_too_short_message_rejected_without_consuming_id(self):
        """AC-A4: Message under 5 characters after trimming is rejected without consuming note ID."""
        short_messages = ["", "hi", "test", "   a   "]
        for msg in short_messages:
            with self.subTest(msg=msg):
                with self.assertRaises(ValueError):
                    add_note(self.open_ticket, author="Kingsley", message=msg)

        # Invariant check
        self.assertEqual(len(self.open_ticket["notes"]), 0)
        self.assertEqual(next_note_id(self.open_ticket), "N001")

    def test_too_long_message_rejected(self):
        """Message exceeding 300 characters is rejected."""
        long_msg = "A" * 301
        with self.assertRaises(ValueError):
            add_note(self.open_ticket, author="Kingsley", message=long_msg)
        self.assertEqual(len(self.open_ticket["notes"]), 0)

    def test_ac_a5_note_on_resolved_ticket_rejected_accepted_after_reopen(self):
        """
        AC-A5: Adding a note to a resolved ticket is rejected.
        After explicit reopen to 'open', note addition succeeds.
        """
        # Step 1: Reject note on resolved ticket
        with self.assertRaises(ValueError) as ctx:
            add_note(self.resolved_ticket, author="Isaac", message="Attempting note on closed ticket.")
        self.assertIn("resolved ticket", str(ctx.exception).lower())
        self.assertEqual(len(self.resolved_ticket["notes"]), 0)

        # Step 2: Reopen ticket
        self.resolved_ticket["status"] = "open"

        # Step 3: Note is now accepted
        note = add_note(self.resolved_ticket, author="Isaac", message="Ticket reopened: issue recurred.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.resolved_ticket["notes"]), 1)

    def test_notes_allowed_on_in_progress_ticket(self):
        """Notes can be added to in_progress tickets."""
        note = add_note(self.in_progress_ticket, author="Gabriel", message="Testing replacement lamp.")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(len(self.in_progress_ticket["notes"]), 1)

    def test_get_ticket_notes_returns_sorted(self):
        """get_ticket_notes returns notes sorted by note_id."""
        self.open_ticket["notes"] = [
            {"note_id": "N002", "author": "B", "message": "Second note."},
            {"note_id": "N001", "author": "A", "message": "First note."},
        ]
        sorted_notes = get_ticket_notes(self.open_ticket)
        self.assertEqual(sorted_notes[0]["note_id"], "N001")
        self.assertEqual(sorted_notes[1]["note_id"], "N002")


if __name__ == "__main__":
    unittest.main()
