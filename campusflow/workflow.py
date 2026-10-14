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

                case 4:
                    print(self.assign_tickets())

                case 5:
                    print(self.update_status())

                case 2 | 3 | 6 | 7:
                    print("This option is not available yet.")

                case 8:
                    print("Exiting...")
                    break


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



    def assign_tickets(self) -> str:
            
            mentors_available = ["Kingsley", "Gabriel", "Godswill", "Isaac"]

            ticket = self.find_ticket()
            
            mentor_picked = self._get_choice("Select Staff to assign", mentors_available)
            

            if isinstance(ticket, str):
                print(ticket)
                return ticket
            
            
            if ticket["assigned_to"].title() == "None":
                ticket["assigned_to"] = mentor_picked
                self._save_tickets()
                return
            if ticket["assigned_to"].title() == mentor_picked:
                return f"Already assigned to {mentor_picked}"

            print(f"confirm assignment from {ticket["assigned_to"]} to {mentor_picked}\n 1. Yes 2. No")
            choice = get_users_choice()
            if choice == 1:
                ticket["assigned_to"] = mentor_picked
                self._save_tickets()
                
            else:
                return

    def update_status(self) -> str:
        ticket = self.find_ticket()

        if isinstance(ticket, str):
            print(ticket)
            return ticket

        status = ticket["status"]
        assigned_to = ticket.get("assigned_to")

        if status == "open":
            if assigned_to is None or assigned_to == "None" or not assigned_to:
                print("Ticket must be assigned before it can move to in-progress.")
                return "Status not updated."

            ticket["status"] = "in-progress"

        elif status == "in-progress":
            ticket["status"] = "resolved"

        elif status == "resolved":
            ticket["status"] = "closed"

        elif status == "closed":
            print("Ticket is already closed.")
            return "Status not updated."

        else:
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
   