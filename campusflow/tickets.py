VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
VALID_URGENCIES = {"low", "medium", "high"}


def calculate_priority(urgency: str, affected_users: int) -> str:
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


def create_ticket(
    tickets: dict[str, dict],
    title: str,
    category: str,
    urgency: str,
    affected_users: int,
) -> dict | str:
    title = str(title).strip()
    if not title:
        return "Title must not be blank."

    category = str(category).strip().title()
    if category not in VALID_CATEGORIES:
        return "Category must be Network, Hardware, Software, or Other."

    urgency = str(urgency).strip().lower()
    if urgency not in VALID_URGENCIES:
        return "Urgency must be low, medium, or high."

    if not isinstance(affected_users, int) or isinstance(affected_users, bool) or affected_users < 1:
        return "Affected users must be a positive integer."

    priority = calculate_priority(urgency, affected_users)

    highest_id = 0
    for key in tickets:
        clean_id = str(key).replace("T", "")
        if clean_id.isdigit():
            number = int(clean_id)
            if number > highest_id:
                highest_id = number

    next_number = highest_id + 1
    ticket_id = f"T{next_number:03d}"

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": "None",
    }

    tickets[ticket_id] = ticket
    return ticket

