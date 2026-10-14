"""
Centralized validation helpers and lifecycle invariants for CampusFlow.
"""

VALID_CATEGORIES = frozenset({"Network", "Hardware", "Software", "Other"})
VALID_URGENCIES = frozenset({"low", "medium", "high"})
VALID_STATUSES = frozenset({"open", "in_progress", "resolved"})


def normalize_category(category: str) -> str:
    """
    Normalizes category to canonical title-case and validates against whitelist.
    Raises ValueError if category is invalid.
    """
    if not isinstance(category, str):
        raise ValueError("Category must be a string.")
    
    clean = category.strip().title()
    if clean not in VALID_CATEGORIES:
        raise ValueError("Category must be Network, Hardware, Software, or Other.")
    return clean


def normalize_urgency(urgency: str) -> str:
    """
    Normalizes urgency to lowercase and validates against whitelist.
    Raises ValueError if urgency is invalid.
    """
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be a string.")
    
    clean = urgency.strip().lower()
    if clean not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")
    return clean


def validate_affected_users(affected_users) -> int:
    """
    Validates affected_users is a strictly positive integer.
    Explicitly rejects booleans (isinstance(True, int) is True), floats, strings,
    and non-positive integers. Raises ValueError on invalid input.
    """
    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a positive integer.")
    
    if affected_users < 1:
        raise ValueError("Affected users must be a positive integer.")
    
    return affected_users


def validate_title(title: str) -> str:
    """
    Validates ticket title is a non-empty string after trimming whitespace.
    Raises ValueError if title is blank or invalid.
    """
    if not isinstance(title, str):
        raise ValueError("Title must be a string.")
    
    clean = title.strip()
    if not clean:
        raise ValueError("Title must not be blank.")
    
    return clean


def validate_ticket_data(title: str, category: str, urgency: str, affected_users: int) -> tuple[str, str, str, int]:
    """
    Validates all core ticket attributes together.
    Returns normalized (title, category, urgency, affected_users) or raises ValueError.
    """
    clean_title = validate_title(title)
    clean_category = normalize_category(category)
    clean_urgency = normalize_urgency(urgency)
    clean_users = validate_affected_users(affected_users)
    return clean_title, clean_category, clean_urgency, clean_users


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
