"""
Structured follow-up notes engine for CampusFlow tickets.
"""

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300


def add_note(ticket: dict, author: str, message: str) -> dict:
    """
    Validates and appends a follow-up note to an open or in_progress ticket.
    If validation fails, returns an error details dictionary:
    {"error": str, "success": False} without raising or halting.
    """

    def _validate_ticket_state() -> str | None:
        if not isinstance(ticket, dict):
            return "Target ticket must be a dictionary."
        status = ticket.get("status")
        if status == "resolved":
            return "Cannot add note to a resolved ticket. Please reopen the ticket first."
        if status not in ("open", "in_progress", "in-progress"):
            return f"Cannot add note to a ticket with status '{status}'."
        return None

    def _validate_and_clean_payload() -> tuple[str | None, str | None, str | None]:
        if not isinstance(author, str):
            return None, None, "Note author must be a string."
        clean_author = author.strip()
        if not clean_author:
            return None, None, "Note author must not be blank."

        if not isinstance(message, str):
            return None, None, "Note message must be a string."
        clean_msg = message.strip()
        if len(clean_msg) < NOTE_MIN_LENGTH or len(clean_msg) > NOTE_MAX_LENGTH:
            return None, None, (
                f"Note message must be between {NOTE_MIN_LENGTH} and {NOTE_MAX_LENGTH} characters after trimming (got {len(clean_msg)})."
            )
        return clean_author, clean_msg, None

    def _generate_note_id() -> str:
        return next_note_id(ticket)

    # 1. Validate ticket state
    ticket_err = _validate_ticket_state()
    if ticket_err:
        return {"error": ticket_err, "success": False}

    # 2. Validate author and message
    clean_author, clean_message, payload_err = _validate_and_clean_payload()
    if payload_err:
        return {"error": payload_err, "success": False}

    # 3. Generate note
    note_id = _generate_note_id()
    note = {
        "note_id": note_id,
        "author": clean_author,
        "message": clean_message,
    }

    if "notes" not in ticket or not isinstance(ticket["notes"], list):
        ticket["notes"] = []

    ticket["notes"].append(note)
    return note


def format_notes_display(ticket: dict) -> str:
    """Format all notes of a ticket into a clean readable string with nested sorting helper."""

    def _extract_sorted_notes() -> list[dict]:
        return get_ticket_notes(ticket)

    notes = _extract_sorted_notes()
    if not notes:
        return f"No follow-up notes found for ticket {ticket.get('id', 'N/A')}."

    lines = [f"--- Follow-up Notes for {ticket.get('id', 'N/A')} ({len(notes)} total) ---"]
    for note in notes:
        lines.append(f"[{note.get('note_id', 'N/A')}] By {note.get('author', 'Anonymous')}:")
        lines.append(f"    {note.get('message', '')}")
    lines.append("-" * 55)
    return "\n".join(lines)


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


def get_ticket_notes(ticket: dict) -> list[dict]:
    """
    Returns the list of follow-up notes for a ticket in ascending order by note_id.
    """
    if not isinstance(ticket, dict):
        return []
    notes = ticket.get("notes") or []
    return sorted(notes, key=lambda n: str(n.get("note_id", "")))

