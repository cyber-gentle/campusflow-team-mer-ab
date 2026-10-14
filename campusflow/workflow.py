from campusflow.reports import generate_ticket_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket as add_ticket



class TicketManager:

    tickets_file_name = "tickets_logs.json"
    admin_only_options = {4, 6, 7}
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
        CAMPUSFLOW HELPDESK         
User: {self.current_user}
====================================
1. Create Ticket
2. List All Tickets
3. View Ticket Details
4. Assign Ticket
5. Update Ticket Status
6. View Work Queue
7. Generate Reports
8. Exit
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
                    print(generate_ticket_report(self.tickets_file_name))

                case 8:
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
            if t.get("status") in ("open", "in-progress", "in_progress")
        ]

        if not active_tickets:
            print("\nNo active tickets in the work queue.")
            return

        active_tickets.sort(
            key=lambda t: priority_rank.get(str(t.get("priority", "")).lower(), 5)
        )

        print("\n================================ WORK QUEUE ================================")
        print(f"{'Priority':<10} {'ID':<8} {'Title':<25} {'Category':<12} {'Status':<12} {'Assigned To':<12}")
        print("-" * 80)
        for ticket in active_tickets:
            assigned = str(ticket.get("assigned_to") or "None")
            title = ticket.get("title", "")
            if len(title) > 22:
                title = title[:21] + "..."
            print(f"{ticket.get('priority', ''):<10} {ticket['id']:<8} {title:<25} {ticket.get('category', ''):<12} {ticket.get('status', ''):<12} {assigned:<12}")
        print("============================================================================")

    def assign_tickets(self) -> str:
        mentors_available = ["Kingsley", "Gabriel", "Godswill", "Isaac"]

        ticket = self.find_ticket()
        if isinstance(ticket, str):
            return ticket

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
            print(ticket)
            return ticket

        status = ticket["status"]
        assigned_to = ticket.get("assigned_to")

        match status:
            case "open":
                if not assigned_to or assigned_to == "None":
                    print("Ticket must be assigned before it can move to in-progress.")
                    return "Status not updated."
                ticket["status"] = "in-progress"

            case "in-progress" | "in_progress":
                ticket["status"] = "resolved"

            case "resolved":
                ticket["status"] = "closed"

            case "closed":
                print("Ticket is already closed.")
                return "Status not updated."

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
   