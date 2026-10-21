"""
Ticket creation, priority calculation, and ID generation for CampusFlow.
"""

from campusflow.validation import (
    VALID_CATEGORIES,
    VALID_STATUSES,
    VALID_URGENCIES,
    validate_ticket_data,
)


def calculate_priority(urgency: str, affected_users: int) -> str:
    """
    Calculates priority strictly following precedence rules:
      1. Critical: high urgency AND >= 10 affected users
      2. High:     high urgency OR >= 10 affected users
      3. Medium:   medium urgency OR >= 3 affected users
      4. Low:      all remaining valid tickets
    """
    urgency = str(urgency).strip().lower()

    match (urgency, affected_users):
        case ("high", n) if n >= 10:
            return "critical"
        case ("high", _):
            return "high"
        case (_, n) if n >= 10:
            return "high"
        case ("medium", _):
            return "medium"
        case (_, n) if n >= 3:
            return "medium"
        case _:
            return "low"


def next_ticket_id(tickets: dict) -> str:
    """
    Calculates the next unique sequential ticket ID (T001, T002, ...)
    by inspecting existing keys in the ticket dictionary.
    """
    highest_id = 0
    for key in tickets:
        clean_id = str(key).replace("T", "")
        if clean_id.isdigit():
            number = int(clean_id)
            if number > highest_id:
                highest_id = number

    return f"T{highest_id + 1:03d}"


def create_ticket(
    tickets: dict[str, dict],
    title: str,
    category: str,
    urgency: str,
    affected_users: int,
    raise_on_error: bool = False,
) -> dict:
    """
    Validates inputs and creates a new ticket.
    Appends the new ticket with 'notes': [] and 'assigned_to': None.
    If validation fails, returns error details dictionary:
    {"error": str(e), "success": False} without halting execution.
    """
    try:
        clean_title, clean_category, clean_urgency, clean_users = validate_ticket_data(
            title, category, urgency, affected_users
        )
    except ValueError as e:
        return {"error": str(e), "success": False}

    priority = calculate_priority(clean_urgency, clean_users)
    ticket_id = next_ticket_id(tickets)

    ticket = {
        "id": ticket_id,
        "title": clean_title,
        "category": clean_category,
        "urgency": clean_urgency,
        "affected_users": clean_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets[ticket_id] = ticket
    return ticket
