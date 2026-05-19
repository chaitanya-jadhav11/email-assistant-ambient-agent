from typing import Literal

from langgraph.constants import END
from langgraph.types import Command

from src.email_assistant.graphs.states.state import MainState
from src.email_assistant.memory.memory import get_memory
from src.email_assistant.models.llm import llm_router
from src.email_assistant.prompts.prompts import triage_user_prompt, triage_system_prompt, default_background, \
    default_triage_instructions
from src.email_assistant.utils.formatter import parse_gmail, format_gmail_markdown


from src.email_assistant.db.db import store, checkpointer, init_db
init_db()

# Nodes
def triage_router(state: MainState) -> Command[Literal["triage_interrupt_handler", "response_agent", "__end__"]]:

    """Analyze email content to decide if we should respond, notify, or ignore.

    The triage step prevents the assistant from wasting time on:
    - Marketing emails and spam
    - Company-wide announcements
    - Messages meant for other teams
    """
    print("----------------------------triage_router----------------------------------")
    email_input = state["email_input"]
    # Parse the email input
    author, to, subject, email_thread, email_id = parse_gmail(email_input)

    user_prompt = triage_user_prompt.format(
        author=author, to=to, subject=subject, email_thread=email_thread
    )

    # Create email markdown for Agent Inbox in case of notification
    email_markdown = format_gmail_markdown(subject, author, to, email_thread, email_id)

    print(f" parse_gmail{parse_gmail(email_input)}")

    # Search for existing triage_preferences memory
    triage_instructions = get_memory(store, ("email_assistant", "triage_preferences"), default_triage_instructions)

    # Format system prompt with background and triage instructions
    system_prompt = triage_system_prompt.format(
        background=default_background,
        triage_instructions=triage_instructions
    )
    # Run the router LLM
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Decision
    classification = result.classification

    print(f" llm classification for received: - {classification}")

    # Process the classification decision
    if classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        # Next node
        goto = "response_agent"
        # Update the state
        update = {
            "classification_decision": result.classification,
            "messages": [{"role": "user",
                          "content": f"Respond to the email: {email_markdown}"
                          }],
        }

    elif classification == "ignore":
        print("🚫 Classification: IGNORE - This email can be safely ignored")

        # Next node
        goto = END
        # Update the state
        update = {
            "classification_decision": classification,
        }

    elif classification == "notify":
        print("🔔 Classification: NOTIFY - This email contains important information")

        # Next node
        goto = "triage_interrupt_handler"
        # Update the state
        update = {
            "classification_decision": classification,
        }

    else:
        raise ValueError(f"Invalid classification: {classification}")

    return Command(goto=goto, update=update)
