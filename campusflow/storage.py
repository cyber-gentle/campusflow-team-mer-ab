"""
Defensive JSON persistence and schema validation for CampusFlow.
"""

import json
import os
import tempfile
from campusflow.tickets import calculate_priority, next_ticket_id
from campusflow.validation import (
    VALID_CATEGORIES,
    VALID_STATUSES,
    VALID_URGENCIES,
    validate_affected_users,
    validate_title,
)

REQUIRED_TICKET_KEYS = frozenset({
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
})

REQUIRED_NOTE_KEYS = frozenset({"note_id", "author", "message"})


def validate_ticket_collection(data: any) -> tuple[bool, str, dict[str, dict]]:
    """
    Performs deep structural and invariant validation on a collection of tickets:
      - Must be a dictionary.
      - Each ticket contains all required keys.
      - Dictionary key must match ticket 'id'.
      - ID format must be valid (T followed by digits).
      - Category and urgency match valid whitelists.
      - Affected users is a positive integer.
      - Priority matches the priority engine calculation strictly.
      - Status is legal (open, in_progress, resolved).
      - Notes is a list of valid note records with unique per-ticket note IDs.
    Returns (is_valid, error_message, sanitized_tickets).
    """
    if not isinstance(data, dict):
        return False, "Tickets data must be a JSON dictionary.", {}

    sanitized = {}

    for key, ticket in data.items():
        if not isinstance(ticket, dict):
            return False, f"Ticket record under key '{key}' is not an object.", {}

        missing_keys = REQUIRED_TICKET_KEYS - set(ticket.keys())
        if missing_keys:
            return False, f"Ticket '{key}' is missing required keys: {sorted(missing_keys)}.", {}

        ticket_id = str(ticket.get("id", "")).strip()
        if key != ticket_id:
            return False, f"Dictionary key '{key}' does not match ticket ID '{ticket_id}'.", {}

        clean_id_num = ticket_id.replace("T", "")
        if not ticket_id.startswith("T") or not clean_id_num.isdigit():
            return False, f"Ticket '{key}' has an invalid ID format (must be T followed by digits).", {}

        try:
            clean_title = validate_title(ticket["title"])
        except ValueError as e:
            return False, f"Ticket '{key}' has invalid title: {e}", {}

        category = str(ticket["category"]).strip().title()
        if category not in VALID_CATEGORIES:
            return False, f"Ticket '{key}' has invalid category '{ticket['category']}'.", {}

        urgency = str(ticket["urgency"]).strip().lower()
        if urgency not in VALID_URGENCIES:
            return False, f"Ticket '{key}' has invalid urgency '{ticket['urgency']}'.", {}

        try:
            affected_users = validate_affected_users(ticket["affected_users"])
        except ValueError as e:
            return False, f"Ticket '{key}' has invalid affected_users: {e}", {}

        expected_priority = calculate_priority(urgency, affected_users)
        actual_priority = str(ticket["priority"]).strip().lower()
        if actual_priority != expected_priority:
            return (
                False,
                f"Ticket '{key}' priority mismatch: expected '{expected_priority}', found '{actual_priority}'.",
                {},
            )

        raw_status = str(ticket["status"]).strip()
        status = "in_progress" if raw_status == "in-progress" else raw_status
        if status not in VALID_STATUSES:
            return False, f"Ticket '{key}' has invalid status '{raw_status}'.", {}

        assigned_to = ticket.get("assigned_to")
        if assigned_to == "None":
            assigned_to = None

        # Notes validation and backward compatibility
        raw_notes = ticket.get("notes")
        if raw_notes is None:
            notes = []
        elif not isinstance(raw_notes, list):
            return False, f"Ticket '{key}' notes must be a list.", {}
        else:
            notes = []
            seen_note_ids = set()
            for note in raw_notes:
                if not isinstance(note, dict):
                    return False, f"Ticket '{key}' contains a non-dict note.", {}

                missing_note_keys = REQUIRED_NOTE_KEYS - set(note.keys())
                if missing_note_keys:
                    return False, f"Note in ticket '{key}' missing keys: {sorted(missing_note_keys)}.", {}

                note_id = str(note["note_id"]).strip()
                if not note_id.startswith("N") or not note_id.replace("N", "").isdigit():
                    return False, f"Note '{note_id}' in ticket '{key}' has invalid ID format.", {}

                if note_id in seen_note_ids:
                    return False, f"Duplicate note ID '{note_id}' found in ticket '{key}'.", {}
                seen_note_ids.add(note_id)

                author = str(note["author"]).strip()
                if not author:
                    return False, f"Note '{note_id}' in ticket '{key}' has a blank author.", {}

                message = str(note["message"]).strip()
                if len(message) < 5 or len(message) > 300:
                    return (
                        False,
                        f"Note '{note_id}' in ticket '{key}' message length ({len(message)}) outside 5–300 limit.",
                        {},
                    )

                notes.append({
                    "note_id": note_id,
                    "author": author,
                    "message": message,
                })

        sanitized[ticket_id] = {
            "id": ticket_id,
            "title": clean_title,
            "category": category,
            "urgency": urgency,
            "affected_users": affected_users,
            "priority": expected_priority,
            "status": status,
            "assigned_to": assigned_to,
            "notes": notes,
        }

    return True, "", sanitized


def save_tickets(file_name: str, tickets: dict[str, dict]) -> str:
    """
    Saves tickets dictionary to disk safely in JSON format.
    Ensures directory exists and performs an atomic write using a temporary file.
    """
    if not isinstance(file_name, str):
        return "Save file name must be a string"

    file_path = f"./data/{file_name}"
    target_dir = os.path.dirname(file_path) or "./data"
    os.makedirs(target_dir, exist_ok=True)

    try:
        # Atomic write to temporary file first, then replace
        dir_name = os.path.dirname(os.path.abspath(file_path))
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as temp_file:
            json.dump(tickets, temp_file, indent=4)
            temp_path = temp_file.name

        os.replace(temp_path, file_path)
        return "\nTicket logged successfully!"
    except Exception as e:
        return f"\nError saving data: {e}"


def load_tickets(file_name: str) -> tuple[str, dict[str, dict]]:
    """
    Defensively loads and validates tickets from disk.
    Guarantees:
      - If file is missing or empty, starts fresh gracefully.
      - If JSON is malformed or invalid records/duplicate IDs exist,
        rejects load completely with an informative error message
        so existing in-memory state is protected.
    Returns (error_message, validated_tickets).
    """
    if not isinstance(file_name, str):
        return "\nFile name must be a string.", {}

    file_path = f"./data/{file_name}"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                return f"\n{file_path} is empty. Starting with a fresh dictionary.", {}
            data = json.loads(content)
    except FileNotFoundError:
        return f"\n{file_path} not found. Starting with a fresh dictionary.", {}
    except json.JSONDecodeError as e:
        return f"\nError: Malformed JSON in {file_path} ({e}). Please inspect file before saving to avoid data loss.", {}

    is_valid, err_msg, validated_tickets = validate_ticket_collection(data)
    if not is_valid:
        return (
            f"\nError: Invalid ticket data in {file_path} ({err_msg}). Rejecting load to prevent data corruption.",
            {},
        )

    return "", validated_tickets
