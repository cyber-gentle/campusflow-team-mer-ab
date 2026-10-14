VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}


def calculate_priority(urgency: str, affected_users: int) -> str:
    urgency = str(urgency).strip().lower()

    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
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

