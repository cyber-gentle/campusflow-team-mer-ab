"""
Unit tests for defensive JSON persistence and schema validation (Engineer A).
Covers: AC-A6, AC-A7, reload integrity, and atomic saves.
"""

import json
import os
import unittest
from campusflow.notes import add_note, next_note_id
from campusflow.storage import load_tickets, save_tickets, validate_ticket_collection
from campusflow.tickets import create_ticket, next_ticket_id


class TestTicketStorage(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_temp_tickets.json"
        self.test_path = f"./data/{self.test_file}"
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def tearDown(self):
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_save_and_reload_preserves_tickets(self):
        """Saving tickets to JSON and reloading preserves all data."""
        tickets = {}
        t1 = create_ticket(tickets, "Library WiFi", "Network", "high", 15)
        t2 = create_ticket(tickets, "Projector Issue", "Hardware", "low", 1)

        save_res = save_tickets(self.test_file, tickets)
        self.assertIn("successfully", save_res.lower())

        msg, loaded_tickets = load_tickets(self.test_file)
        self.assertEqual(len(loaded_tickets), 2)
        self.assertEqual(loaded_tickets["T001"]["title"], "Library WiFi")
        self.assertEqual(loaded_tickets["T002"]["title"], "Projector Issue")

    def test_missing_file_starts_fresh_without_error(self):
        """Missing file returns an informative message and a fresh dictionary."""
        msg, loaded_tickets = load_tickets("non_existent_file.json")
        self.assertEqual(loaded_tickets, {})
        self.assertIn("not found", msg.lower())

    def test_empty_file_starts_fresh_dictionary(self):
        """An empty file returns fresh dictionary gracefully."""
        os.makedirs("./data", exist_ok=True)
        with open(self.test_path, "w") as f:
            f.write("")

        msg, loaded_tickets = load_tickets(self.test_file)
        self.assertEqual(loaded_tickets, {})
        self.assertIn("empty", msg.lower())

    def test_ac_a6_malformed_json_produces_clear_error_and_preserves_state(self):
        """AC-A6: Corrupted/malformed JSON produces an explicit error message instead of silently erasing data."""
        os.makedirs("./data", exist_ok=True)
        with open(self.test_path, "w") as f:
            f.write("{ invalid json content: 123 ")

        # Active memory before load attempt
        in_memory_state = {"T001": {"id": "T001", "title": "Critical Server"}}

        msg, loaded_tickets = load_tickets(self.test_file)
        # Verify load was rejected
        self.assertEqual(loaded_tickets, {})
        self.assertIn("malformed json", msg.lower())

        # If caller follows the contract (if not msg: self.tickets = loaded_tickets),
        # in_memory_state is protected from overwrite
        if not msg:
            in_memory_state = loaded_tickets
        self.assertIn("T001", in_memory_state, "In-memory state must be preserved")

    def test_ac_a6_invalid_ticket_schema_rejected(self):
        """AC-A6: Records with invalid priority or missing keys are rejected."""
        os.makedirs("./data", exist_ok=True)
        invalid_data = {
            "T001": {
                "id": "T001",
                "title": "Bad Priority Ticket",
                "category": "Network",
                "urgency": "high",
                "affected_users": 20,
                "priority": "low",  # Mismatch! High+20 should be critical
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        }
        with open(self.test_path, "w") as f:
            json.dump(invalid_data, f)

        msg, loaded = load_tickets(self.test_file)
        self.assertEqual(loaded, {})
        self.assertIn("priority mismatch", msg.lower())

    def test_ac_a7_reload_preserves_notes_and_continues_next_ticket_and_note_ids(self):
        """
        AC-A7: Reloading tickets properly preserves follow-up notes and ensures
        next ticket ID and note IDs continue sequentially without collisions.
        """
        tickets = {}
        t1 = create_ticket(tickets, "Core Router Reboot", "Network", "high", 15)
        add_note(t1, author="Kingsley", message="Attempted remote reboot; switch unresponsive.")

        t2 = create_ticket(tickets, "Printer Toner Out", "Hardware", "low", 2)
        save_tickets(self.test_file, tickets)

        # Reload from storage
        msg, loaded = load_tickets(self.test_file)
        self.assertEqual(msg, "")
        self.assertEqual(len(loaded), 2)
        self.assertEqual(len(loaded["T001"]["notes"]), 1)
        self.assertEqual(loaded["T001"]["notes"][0]["note_id"], "N001")

        # Invariant 1: next ticket ID continues sequentially
        self.assertEqual(next_ticket_id(loaded), "T003")
        t3 = create_ticket(loaded, "New Ticket Post Reload", "Software", "medium", 4)
        self.assertEqual(t3["id"], "T003")

        # Invariant 2: next note ID on loaded ticket continues sequentially
        self.assertEqual(next_note_id(loaded["T001"]), "N002")
        new_note = add_note(loaded["T001"], author="Gabriel", message="Dispatched technician to site.")
        self.assertEqual(new_note["note_id"], "N002")
        self.assertEqual(len(loaded["T001"]["notes"]), 2)


if __name__ == "__main__":
    unittest.main()
