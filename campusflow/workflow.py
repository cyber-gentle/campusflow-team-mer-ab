from .storage import load_tickets, save_tickets
from .tickets import create_ticket as add_ticket


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

            if users_choice == 1:
                self.create_ticket()
            elif users_choice == 8:
                print("Exiting...")
                break
            elif users_choice in range(2, 8):
                if self.current_user == "standard_user" and users_choice in self.admin_only_options:
                    print("This option is restricted to administrators.")
                else:
                    print("This option is not available yet.")
            else:
                print("Choose a valid input.")

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


def get_users_choice() -> int:
    users_choice = input("Enter your choice: ")

    try:
        return int(users_choice)
    except ValueError:
        return 0
