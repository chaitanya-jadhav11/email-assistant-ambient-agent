
from src.email_assistant.graphs.states.state import MainState
from src.email_assistant.tools.gmail.gmail_tools import mark_as_read
from src.email_assistant.utils.formatter import parse_gmail


def mark_as_read_node(state: MainState):
    print("------------------------------In mark_as_read_node------------------------------------")
    email_input = state["email_input"]
    author, to, subject, email_thread, email_id = parse_gmail(email_input)
    print(f"------------------------------Marking below Email subject as read- {subject} ")
    mark_as_read(email_id)
