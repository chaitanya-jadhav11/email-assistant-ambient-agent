from typing import Literal

from langgraph.store.base import BaseStore

from src.email_assistant.graphs.states.state import MainState


def should_continue(state: MainState, store: BaseStore) -> Literal["interrupt_handler", "mark_as_read_node"]:
    """Route to tool handler, or end if Done tool called"""

    messages = state["messages"]
    print("---------------------should_continue---------------------.. ")

    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "Done":
                return "mark_as_read_node"
            else:
                return "interrupt_handler"