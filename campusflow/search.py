"""Multi-filter search engine for CampusFlow Next (Engineer B).

Provides read-only substring matching and logical AND filter composition
over ticket collections without mutating original records.
"""

PRIORITY_RANK = {"critical": 1, "high": 2, "medium": 3, "low": 4}


def filter_tickets(
    tickets: dict[str, dict] | list[dict],
    title: str = "",
    category: str = "",
    status: str = "",
    priority: str = "",
) -> list[dict]:
    """Filter tickets using case-insensitive substring on title and exact filter matching.
    
    All supplied non-empty filters must match (logical AND).
    Empty or whitespace-only filters are skipped.
    Guarantees read-only semantics: does not modify any ticket dictionary.
    """
    records = list(tickets.values()) if isinstance(tickets, dict) else list(tickets)
    
    normalized_title = title.strip().casefold() if title else ""
    normalized_category = category.strip().title() if category else ""
    normalized_status = status.strip().lower() if status else ""
    normalized_priority = priority.strip().lower() if priority else ""

    results = []
    for ticket in records:
        # Title check (case-insensitive substring with hyphen flexibility)
        if normalized_title:
            ticket_title = str(ticket.get("title", "")).casefold()
            match_direct = normalized_title in ticket_title
            match_unhyphen = normalized_title.replace("-", "") in ticket_title.replace("-", "")
            if not (match_direct or match_unhyphen):
                continue

        # Category check
        if normalized_category:
            ticket_cat = str(ticket.get("category", "")).strip().title()
            if ticket_cat != normalized_category:
                continue

        # Status check (handles in_progress and in-progress normalization)
        if normalized_status:
            t_status = str(ticket.get("status", "")).strip().lower().replace("-", "_")
            n_status = normalized_status.replace("-", "_")
            if t_status != n_status:
                continue

        # Priority check
        if normalized_priority:
            ticket_priority = str(ticket.get("priority", "")).strip().lower()
            if ticket_priority != normalized_priority:
                continue

        # All supplied filters matched
        results.append(ticket)

    return results


def sort_tickets_by_priority(tickets: list[dict]) -> list[dict]:
    """Sort search results by priority (critical > high > medium > low),
    breaking ties using earlier numeric ticket ID.
    """
    def _sort_key(t: dict):
        rank = PRIORITY_RANK.get(str(t.get("priority", "")).lower(), 5)
        raw_id = str(t.get("id", "")).replace("T", "")
        numeric_id = int(raw_id) if raw_id.isdigit() else 999999
        return (rank, numeric_id)

    return sorted(tickets, key=_sort_key)
