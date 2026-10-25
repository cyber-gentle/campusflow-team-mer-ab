from campusflow.reports import generate_ticket_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket as add_ticket
from campusflow.search import filter_tickets, sort_tickets_by_priority
from campusflow.notes import add_note, format_notes_display
from campusflow.understanding_check import run_understanding_check
from campusflow.validation import validate_ticket_id



class TicketManager:

    tickets_file_name = "tickets_logs.json"
    admin_only_options = {4, 6, 10}
    categories = ("Network", "Hardware", "Software", "Other")
    urgencies = ("low", "medium", "high")
    user_roles = ("administrator", "standard_user")

    def __init__(self):
        self.tickets_file_name = self.__class__.tickets_file_name
        message, self.tickets = load_tickets(self.tickets_file_name)
        if message:
            print(message)
        self.current_user = None

    def run_menu(self):
        self.current_user = self.check_user()
        print(f"\nLogged in as: {self.current_user}")

        while True:
            print(f"""
====================================
        CAMPUSFLOW NEXT             
User: {self.current_user}
====================================
1. Create Ticket
2. List All Tickets
3. View Ticket Details
4. Assign Ticket
5. Update Ticket Status
6. View Open Work Queue
7. Search Tickets (Multi-Filter)
8. Add Follow-up Note
9. View Ticket Notes
10. Generate Reports
11. Engineering Understanding Check
12. Exit
====================================
""")
            users_choice = get_users_choice()

            match users_choice:
                case _ if self.current_user == "standard_user" and users_choice in self.admin_only_options:
                    print("This option is restricted to administrators.")

                case 1:
                    self.create_ticket()

                case 2:
                    self.list_all_tickets()

                case 3:
                    self.view_ticket_details()

                case 4:
                    print(self.assign_tickets())

                case 5:
                    print(self.update_status())

                case 6:
                    self.view_work_queue()

                case 7:
                    self.search_tickets_menu()

                case 8:
                    self.add_follow_up_note()

                case 9:
                    self.view_ticket_notes()

                case 10:
                    print(generate_ticket_report(self.tickets_file_name))

                case 11:
                    run_understanding_check()

                case 12:
                    print("Exiting...")
                    break

                case _:
                    print("Select a valid choice.")


    def create_ticket(self):
        title = input("Enter ticket title: ").strip()
        while not title:
            print("Title must not be blank.")
            title = input("Enter ticket title: ").strip()

        category = self._get_choice("Select category", self.categories)
        urgency = self._get_choice("Select urgency", self.urgencies)

        while True:
            try:
                affected_users = int(input("Enter number of affected users: "))
                if affected_users >= 1:
                    break
                print("Affected users must be a positive integer.")
            except ValueError:
                print("Affected users must be a positive integer.")

        ticket = add_ticket(
            self.tickets, title, category, urgency, affected_users
        )
        if isinstance(ticket, dict) and ticket.get("error"):
            print(f"Error: {ticket['error']}")
            return

        self._save_tickets()
        print(f"Created ticket {ticket['id']}.")

    def check_user(self) -> str:
        return self._get_choice("Select user", self.user_roles)
        

    def _get_choice(self, prompt, options):
        while True:
            print(f"\n----->{prompt}<-----")
            for index, option in enumerate(options, start=1):
                print(f"{index}. {option}")

            choice = input("Enter choice: ").strip()
            try:
                choice_index = int(choice)
                if 1 <= choice_index <= len(options):
                    return options[choice_index - 1]
                print("Select a valid choice.")
            except ValueError:
                print("Select a valid choice.")




    def _save_tickets(self):
        print(save_tickets(self.tickets_file_name, self.tickets))



    def find_ticket(self) -> dict | str:
        ticket_id = input("Enter ticket ID: ").upper().strip()
        if not validate_ticket_id(ticket_id):
            return "Invalid ticket ID format. Expected format: T001."
        ticket = self.tickets.get(ticket_id)

        if ticket is None:
            return "Ticket not found."

        return ticket



    def list_all_tickets(self):
        if not self.tickets:
            print("\nNo tickets logged!")
            return

        print(f"\n{'ID':<8} {'Title':<25} {'Category':<12} {'Priority':<10} {'Status':<12} {'Assigned To':<12}")
        print("-" * 80)
        for ticket in self.tickets.values():
            assigned = str(ticket.get("assigned_to") or "None")
            title = ticket.get("title", "")
            if len(title) > 22:
                title = title[:21] + "..."
            print(f"{ticket['id']:<8} {title:<25} {ticket.get('category', ''):<12} {ticket.get('priority', ''):<10} {ticket.get('status', ''):<12} {assigned:<12}")

    def view_ticket_details(self):
        ticket = self.find_ticket()
        if isinstance(ticket, str):
            print(ticket)
            return

        print(f"""
------------------------------------
           TICKET DETAILS           
------------------------------------
ID:             {ticket['id']}
Title:          {ticket.get('title', '')}
Category:       {ticket.get('category', '')}
Urgency:        {ticket.get('urgency', '')}
Affected Users: {ticket.get('affected_users', '')}
Priority:       {ticket.get('priority', '')}
Status:         {ticket.get('status', '')}
Assigned To:    {ticket.get('assigned_to') or 'None'}
------------------------------------""")

    def view_work_queue(self):
        priority_rank = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        active_tickets = [
            t for t in self.tickets.values()
            if str(t.get("status", "")).strip().lower() == "open"
        ]

        if not active_tickets:
            print("\nNo active tickets in the work queue.")
            return

        def _sort_key(ticket):
            rank = priority_rank.get(str(ticket.get("priority", "")).lower(), 5)
            ticket_id_str = str(ticket.get("id", "")).replace("T", "")
            ticket_num = int(ticket_id_str) if ticket_id_str.isdigit() else 999999
            return (rank, ticket_num)

        active_tickets.sort(key=_sort_key)

        print("\n============================== OPEN WORK QUEUE =============================")
        print(f"{'Priority':<10} {'ID':<8} {'Title':<25} {'Category':<12} {'Status':<12} {'Assigned To':<12}")
        print("-" * 80)
        for ticket in active_tickets:
            assigned = str(ticket.get("assigned_to") or "None")
            title = ticket.get("title", "")
            if len(title) > 22:
                title = title[:21] + "..."
            print(f"{ticket.get('priority', ''):<10} {ticket['id']:<8} {title:<25} {ticket.get('category', ''):<12} {ticket.get('status', ''):<12} {assigned:<12}")
        print("============================================================================")

    def search_tickets_menu(self):
        print("\n========================= SEARCH TICKETS =========================")
        print("Leave any filter blank (press Enter) to skip filtering by that field.")
        title_q = input("Search by Title substring: ").strip()

        print("\nFilter by Category (Network / Hardware / Software / Other) or Enter to skip:")
        category_q = input("Category: ").strip()

        print("\nFilter by Status (open / in_progress / resolved) or Enter to skip:")
        status_q = input("Status: ").strip()

        print("\nFilter by Priority (critical / high / medium / low) or Enter to skip:")
        priority_q = input("Priority: ").strip()

        matches = filter_tickets(
            self.tickets,
            title=title_q,
            category=category_q,
            status=status_q,
            priority=priority_q,
        )

        if not matches:
            print("\nNo matching tickets found.")
            return

        print(f"\nFound {len(matches)} matching ticket(s).")
        sort_choice = input("Sort results by Priority and numeric ID? (1. Yes / 2. No): ").strip()
        if sort_choice == "1":
            matches = sort_tickets_by_priority(matches)

        print(f"\n{'ID':<8} {'Title':<25} {'Category':<12} {'Priority':<10} {'Status':<12} {'Assigned To':<12}")
        print("-" * 80)
        for ticket in matches:
            assigned = str(ticket.get("assigned_to") or "None")
            title = ticket.get("title", "")
            if len(title) > 22:
                title = title[:21] + "..."
            print(f"{ticket['id']:<8} {title:<25} {ticket.get('category', ''):<12} {ticket.get('priority', ''):<10} {ticket.get('status', ''):<12} {assigned:<12}")

    def add_follow_up_note(self):
        ticket = self.find_ticket()
        if isinstance(ticket, str):
            print(ticket)
            return

        status = str(ticket.get("status", "")).strip().lower().replace("-", "_")
        if status not in ("open", "in_progress"):
            print(f"Error: Cannot add notes to ticket in '{ticket.get('status')}' status. Reopen ticket first.")
            return

        author = input("Enter your name (author): ").strip()
        while not author:
            print("Author cannot be blank.")
            author = input("Enter your name (author): ").strip()

        message = input("Enter follow-up note message (5-300 characters): ").strip()
        while len(message) < 5 or len(message) > 300:
            print(f"Message length ({len(message)}) must be between 5 and 300 characters.")
            message = input("Enter follow-up note message (5-300 characters): ").strip()

        result = add_note(ticket, author, message)
        if isinstance(result, dict) and not result.get("error"):
            self._save_tickets()
            print(f"Successfully added note [{result['note_id']}] to ticket {ticket['id']}.")
        else:
            err_msg = result.get("error") if isinstance(result, dict) else result
            print(f"Failed to add note: {err_msg}")

    def view_ticket_notes(self):
        ticket = self.find_ticket()
        if isinstance(ticket, str):
            print(ticket)
            return

        print("\n" + format_notes_display(ticket))

    def assign_tickets(self) -> str:
        mentors_available = ["Kingsley", "Gabriel", "Godswill", "Isaac"]

        ticket = self.find_ticket()
        if isinstance(ticket, str):
            return ticket

        if ticket.get("status") == "resolved":
            return "Cannot assign or reassign a resolved ticket. Please reopen the ticket first."

        mentor_picked = self._get_choice("Select Staff to assign", mentors_available)
        current_assigned = str(ticket.get("assigned_to") or "None")

        if current_assigned in ("None", ""):
            ticket["assigned_to"] = mentor_picked
            self._save_tickets()
            return f"Ticket {ticket['id']} successfully assigned to {mentor_picked}."

        if current_assigned == mentor_picked:
            return f"Already assigned to {mentor_picked}."

        print(f"Confirm assignment from {current_assigned} to {mentor_picked}\n 1. Yes \n 2. No")
        choice = get_users_choice()
        if choice == 1:
            ticket["assigned_to"] = mentor_picked
            self._save_tickets()
            return f"Ticket {ticket['id']} successfully reassigned to {mentor_picked}."
        else:
            return "Assignment cancelled."

    def update_status(self) -> str:
        ticket = self.find_ticket()

        if isinstance(ticket, str):
            return ticket

        status = ticket["status"]
        assigned_to = ticket.get("assigned_to")

        match status:
            case "open":
                if not assigned_to or assigned_to == "None":
                    print("Ticket must be assigned before it can move to in-progress.")
                    return "Status not updated."
                ticket["status"] = "in_progress"

            case "in-progress" | "in_progress":
                ticket["status"] = "resolved"

            case "resolved":
                print(f"Ticket {ticket['id']} is currently resolved. Reopen to 'open'?\n 1. Yes \n 2. No")
                choice = get_users_choice()
                if choice == 1:
                    ticket["status"] = "open"
                    self._save_tickets()
                    return f"Ticket {ticket['id']} successfully reopened and set to 'open'."
                return "Resolved ticket was not modified."

            case _:
                print("Invalid ticket status.")
                return "Status not updated."

        self._save_tickets()
        return (f"Ticket status successfully updated to '{ticket['status']}'.")
        
        
            
def get_users_choice() -> int:
    users_choice = input("Enter your choice: ")

    try:
        return int(users_choice)
    except ValueError:
        return 0
   