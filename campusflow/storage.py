import json

def save_tickets(file_name: str, tickets: dict[str, dict]) -> str:
    if not isinstance(file_name, str):
        return "Save file name must be a string"

    file_path = f"./data/{file_name}"
    try:
        with open(file_path, 'w') as file:
            json.dump(tickets, file, indent=4)
        return "\nTicket logged successfully!"
    except (FileNotFoundError):
        return f"{file_name} not found"
    except Exception as e:
        return f"\nError saving data: {e}"


def load_tickets(file_name: str) -> tuple[str, dict[str, dict]]:
    if not isinstance(file_name, str):
        return "\nfile name must be a string.", {}
    
    file_path = f"./data/{file_name}"

    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            if not content:
                return f"\n{file_path} is empty. Starting with a fresh dictionary.", {}
            return "", json.loads(content)
    except FileNotFoundError:
        return f"\n{file_path} not found. Starting with a fresh dictionary.", {}
    except json.JSONDecodeError as e:
        return f"\nError: Malformed JSON in {file_path} ({e}). Please inspect file before saving to avoid data loss.", {}


