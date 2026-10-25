"""
Centralized validation helpers and lifecycle invariants for CampusFlow.
"""

import re

VALID_CATEGORIES = frozenset({"Network", "Hardware", "Software", "Other"})
VALID_URGENCIES = frozenset({"low", "medium", "high"})
VALID_STATUSES = frozenset({"open", "in_progress", "resolved"})
TICKET_ID_REGEX = re.compile(r"T\d{3,}")


def validate_ticket_id(ticket_id: str) -> bool:
    """
    Validates ticket ID format: must start with 'T' followed by at least 3 digits (e.g. T001, T042, T1000).
    """
    if not isinstance(ticket_id, str):
        return False
    return bool(TICKET_ID_REGEX.fullmatch(ticket_id.strip()))



def validate_ticket_data(title: str, category: str, urgency: str, affected_users: int) -> dict:
    """
    Validates and normalizes all core ticket attributes together.
    Returns:
      On success: {"title": str, "category": str, "urgency": str, "affected_users": int, "success": True}
      On failure: {"error": str, "success": False}
    Does NOT raise exceptions.
    """
    # 1. Title validation
    if not isinstance(title, str):
        return {"error": "Title must be a string.", "success": False}
    clean_title = title.strip()
    if not clean_title:
        return {"error": "Title must not be blank.", "success": False}

    # 2. Category normalization & whitelist
    if not isinstance(category, str):
        return {"error": "Category must be a string.", "success": False}
    clean_category = category.strip().title()
    if clean_category not in VALID_CATEGORIES:
        return {"error": "Category must be Network, Hardware, Software, or Other.", "success": False}

    # 3. Urgency normalization & whitelist
    if not isinstance(urgency, str):
        return {"error": "Urgency must be a string.", "success": False}
    clean_urgency = urgency.strip().lower()
    if clean_urgency not in VALID_URGENCIES:
        return {"error": "Urgency must be low, medium, or high.", "success": False}

    # 4. Strictly positive integer affected users (reject booleans, floats, non-integers, <= 0)
    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        return {"error": "Affected users must be a positive integer.", "success": False}
    if affected_users < 1:
        return {"error": "Affected users must be a positive integer.", "success": False}

    return {
        "title": clean_title,
        "category": clean_category,
        "urgency": clean_urgency,
        "affected_users": affected_users,
        "success": True,
    }


def validate_assignment(ticket: dict, staff: str) -> tuple[bool, str]:
    """
    Validates assigning staff to a ticket.
    Guarantees:
      - A resolved ticket cannot accept assignment changes unless explicitly reopened.
      - Staff name must be non-empty.
    Returns (is_valid, message).
    """
    if not isinstance(ticket, dict):
        return False, "Ticket must be a dictionary."

    status = ticket.get("status")
    if status == "resolved":
        return False, "Cannot assign or reassign a resolved ticket. Please reopen the ticket first."

    if not isinstance(staff, str) or not staff.strip():
        return False, "Staff name must not be blank."

    return True, "Assignment valid."


def can_transition(ticket: dict, target_status: str) -> tuple[bool, str]:
    """
    Validates whether a ticket can transition to target_status.
    Enforces invariants:
      - Unassigned open tickets cannot move to in_progress.
      - open -> in_progress (requires assignment) -> resolved.
      - resolved can only reopen to open.
    Returns (can_move, reason).
    """
    if not isinstance(ticket, dict):
        return False, "Invalid ticket record."

    current_status = ticket.get("status")
    assigned_to = ticket.get("assigned_to")

    # Normalize status representation
    if current_status == "in-progress":
        current_status = "in_progress"
    if target_status == "in-progress":
        target_status = "in_progress"

    if target_status not in VALID_STATUSES:
        return False, f"Invalid target status: '{target_status}'."

    if current_status == target_status:
        return False, f"Ticket is already '{current_status}'."

    match (current_status, target_status):
        case ("open", "in_progress"):
            if not assigned_to or assigned_to == "None":
                return False, "Ticket must be assigned before it can move to in-progress."
            return True, "Valid transition from open to in_progress."

        case ("in_progress", "resolved"):
            return True, "Valid transition from in_progress to resolved."

        case ("resolved", "open"):
            return True, "Valid reopen transition from resolved to open."

        case ("resolved", "in_progress"):
            return False, "Resolved ticket cannot move directly to in_progress. Please reopen to open first."

        case ("open", "resolved"):
            return False, "Open ticket must be in_progress before it can be resolved."

        case _:
            return False, f"Illegal transition from '{current_status}' to '{target_status}'."
