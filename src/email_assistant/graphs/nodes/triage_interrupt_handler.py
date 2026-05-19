from typing import Literal

from langgraph.constants import END
from langgraph.types import Command, interrupt

from src.email_assistant.graphs.states.state import MainState


def triage_interrupt_handler(state: MainState) -> Command[Literal["response_agent", "__end__"]]:
    print("-----------------In triage_interrupt_handler----------------------")
    # Send to Agent Inbox and wait for response

    request = {
        "action_request": {
            "action": f"Email Assistant: {state['classification_decision']}",
            "args": {}
        },
        "config": {
            "allow_ignore": True,
            "allow_respond": True,
            "allow_edit": False,
            "allow_accept": False,
        },
        # Email to show in Agent Inbox
        "description": "email_markdown",
    }

    response = interrupt(request)
    print("triage_interrupt_handler: response:", response)
    return Command(goto=END, update="end")

