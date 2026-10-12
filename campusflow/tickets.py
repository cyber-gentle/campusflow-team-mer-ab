def calculate_priority(urgency: str, affected_users: int) -> str:
    if not isinstance(urgency, str):
        return "Urgency must be low, medium, or high."
    urgency = urgency.strip().lower()
    if urgency not in ["low", "medium", "high"]:
        return "Urgency must be low, medium, or high."
    if not isinstance(affected_users, int) or isinstance(affected_users, bool):
        return "Affected users must be a positive integer."
    if affected_users < 1:
        return "Affected users must be a positive integer."

    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def create_ticket(tickets, title, category, urgency, affected_users):
    title = str(title).strip()
    if not title:
        return "Title must not be blank."

    valid_categories = ["Network", "Hardware", "Software", "Other"]
    category = str(category).strip().title()
    if category not in valid_categories:
        return "Category must be Network, Hardware, Software, or Other."

    urgency = str(urgency).strip().lower()

    priority = calculate_priority(urgency, affected_users)

    next_number = len(tickets) + 1
    ticket_id = f"T{next_number:03d}"

    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets[ticket_id[1:]] = ticket
    return ticket
