import os
import unittest
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


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

    def test_malformed_json_produces_clear_error(self):
        """Corrupted/malformed JSON produces an explicit error message instead of silently erasing data."""
        os.makedirs("./data", exist_ok=True)
        with open(self.test_path, "w") as f:
            f.write("{ invalid json content: 123 ")

        msg, loaded_tickets = load_tickets(self.test_file)
        self.assertEqual(loaded_tickets, {})
        self.assertIn("malformed json", msg.lower())

    def test_create_ticket_after_reload_without_duplicate_id(self):
        """After loading saved tickets, new ticket gets the next unique numeric ID."""
        tickets = {}
        create_ticket(tickets, "Existing Ticket", "Network", "low", 1)
        save_tickets(self.test_file, tickets)

        _, loaded = load_tickets(self.test_file)
        new_ticket = create_ticket(loaded, "New Ticket After Reload", "Software", "medium", 4)
        self.assertEqual(new_ticket["id"], "T002")
        self.assertIn("T001", loaded)
        self.assertIn("T002", loaded)


if __name__ == "__main__":
    unittest.main()
