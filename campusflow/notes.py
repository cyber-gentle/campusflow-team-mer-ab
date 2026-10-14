"""
Structured follow-up notes engine for CampusFlow tickets.
"""

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300


def next_note_id(ticket: dict) -> str:
    """
    Calculates the next deterministic note ID (N001, N002, ...) for a ticket.
    Inspects existing notes to determine the maximum existing numeric suffix.
    """
    if not isinstance(ticket, dict):
        return "N001"

    notes = ticket.get("notes") or []
    highest_id = 0
    for note in notes:
        if isinstance(note, dict):
            raw_id = str(note.get("note_id", "")).replace("N", "")
            if raw_id.isdigit():
                num = int(raw_id)
                if num > highest_id:
                    highest_id = num

    return f"N{highest_id + 1:03d}"


def add_note(ticket: dict, author: str, message: str) -> dict:
    """
    Validates and appends a follow-up note to an open or in_progress ticket.
    Raises ValueError if:
      - ticket is resolved or invalid
      - author is blank after trimming
      - message length is not within 5 to 300 characters after trimming
    Guarantees:
      - Rejected attempts never consume a note ID.
      - In-memory ticket remains completely unchanged on validation failure.
    Returns the created note dictionary.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Target ticket must be a dictionary.")

    status = ticket.get("status")
    if status == "resolved":
        raise ValueError("Cannot add note to a resolved ticket. Please reopen the ticket first.")

    if status not in ("open", "in_progress", "in-progress"):
        raise ValueError(f"Cannot add note to a ticket with status '{status}'.")

    # Author validation
    if not isinstance(author, str):
        raise ValueError("Note author must be a string.")
    clean_author = author.strip()
    if not clean_author:
        raise ValueError("Note author must not be blank.")

    # Message validation
    if not isinstance(message, str):
        raise ValueError("Note message must be a string.")
    clean_message = message.strip()
    if len(clean_message) < NOTE_MIN_LENGTH or len(clean_message) > NOTE_MAX_LENGTH:
        raise ValueError(
            f"Note message must be between {NOTE_MIN_LENGTH} and {NOTE_MAX_LENGTH} characters after trimming (got {len(clean_message)})."
        )

    # All validations passed; generate ID and append note
    note_id = next_note_id(ticket)
    note = {
        "note_id": note_id,
        "author": clean_author,
        "message": clean_message,
    }

    if "notes" not in ticket or not isinstance(ticket["notes"], list):
        ticket["notes"] = []

    ticket["notes"].append(note)
    return note


def get_ticket_notes(ticket: dict) -> list[dict]:
    """
    Returns the list of follow-up notes for a ticket in ascending order by note_id.
    """
    if not isinstance(ticket, dict):
        return []
    notes = ticket.get("notes") or []
    return sorted(notes, key=lambda n: str(n.get("note_id", "")))
