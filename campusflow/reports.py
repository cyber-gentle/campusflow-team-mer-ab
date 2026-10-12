from campusflow.storage import load_tickets
def generate_ticket_report(data_file_name: str) -> str:
    """Generate a summary of all tickets."""
    message, tickets = load_tickets(data_file_name)

    if message:
        print(message)

    total_tickets = 0

    by_status = {
        "open": 0, "in_progress": 0, "resolved": 0}
    
    by_priority = {
        "critical": 0, "high" : 0, "medium": 0, "low": 0
    }

    if not tickets:
        return "No ticket logged!"

    for ticket in tickets.values():

        if ticket["status"] == "open":
            by_status["open"] += 1

        elif ticket["status"] == "in_progress" or ticket["status"] == "in-progress":
            by_status["in_progress"] += 1

        elif ticket["status"] == "resolved":
            by_status["resolved"] += 1

        if ticket["priority"] == "critical":
            by_priority["critical"] += 1

        elif ticket["priority"] == "high":
            by_priority["high"] += 1
    
        elif ticket["priority"] == "medium":
            by_priority["medium"] += 1

        elif ticket["priority"] == "low":
            by_priority["low"] += 1

        total_tickets += 1


    return f"""
Metric                      Status               Ticket Count
-----------------------------------------------------------------------
Total Tickets               All Active & Closed     {total_tickets}
-----------------------------------------------------------------------
By Status                   Open                    {by_status['open']}
                            In Progress             {by_status['in_progress']}
                            Resolved                {by_status['resolved']}
-----------------------------------------------------------------------
By Priority                 Critical                {by_priority['critical']}
                            High                    {by_priority['high']}
                            Medium                  {by_priority['medium']}
                            Low                     {by_priority['low']}
------------------------------------------------------------------------
"""