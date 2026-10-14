"""Reports and analytics engine for CampusFlow Next (Engineer B).

Provides trustworthy metrics: total counts, status, priority, category breakdowns,
unresolved vs resolved counts, and resolution percentage (0% for empty dataset).
"""

from campusflow.storage import load_tickets


def generate_ticket_report(data_source: str | dict[str, dict]) -> str:
    """Generate a trustworthy summary report of all tickets.
    
    Accepts either a JSON filename (str) or an in-memory tickets dict.
    Guarantees no ZeroDivisionError on empty datasets and displays 0.0%.
    """
    if isinstance(data_source, str):
        message, tickets = load_tickets(data_source)
    else:
        tickets = data_source or {}

    total_tickets = len(tickets)

    by_status = {"open": 0, "in_progress": 0, "resolved": 0}
    by_priority = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    by_category = {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0}

    for ticket in tickets.values():
        # Status count
        status_key = str(ticket.get("status", "")).strip().lower().replace("-", "_")
        if status_key in by_status:
            by_status[status_key] += 1
        else:
            by_status["open"] += 1

        # Priority count
        priority_key = str(ticket.get("priority", "")).strip().lower()
        if priority_key in by_priority:
            by_priority[priority_key] += 1
        else:
            by_priority["low"] += 1

        # Category count
        category_key = str(ticket.get("category", "")).strip().title()
        if category_key in by_category:
            by_category[category_key] += 1
        else:
            by_category["Other"] += 1

    unresolved_count = by_status["open"] + by_status["in_progress"]
    resolved_count = by_status["resolved"]
    resolution_pct = (resolved_count / total_tickets * 100) if total_tickets > 0 else 0.0

    return f"""
=======================================================================
                     CAMPUSFLOW TRUSTED METRICS REPORT                 
=======================================================================
Metric                      Category / State         Count / Percentage
-----------------------------------------------------------------------
Total Tickets               All Active & Closed      {total_tickets}
Resolution Rate             Resolved / Total         {resolution_pct:.1f}%
Unresolved Active           Open + In Progress       {unresolved_count}
Resolved Completed          Closed Lifecycle         {resolved_count}
-----------------------------------------------------------------------
By Status                   Open                     {by_status['open']}
                            In Progress              {by_status['in_progress']}
                            Resolved                 {by_status['resolved']}
-----------------------------------------------------------------------
By Priority                 Critical                 {by_priority['critical']}
                            High                     {by_priority['high']}
                            Medium                   {by_priority['medium']}
                            Low                      {by_priority['low']}
-----------------------------------------------------------------------
By Category                 Network                  {by_category['Network']}
                            Hardware                 {by_category['Hardware']}
                            Software                 {by_category['Software']}
                            Other                    {by_category['Other']}
=======================================================================
"""