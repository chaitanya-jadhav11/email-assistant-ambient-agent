from src.email_assistant.db.db import store
from src.email_assistant.graphs.states.state import MainState
from src.email_assistant.memory.memory import get_memory
from src.email_assistant.models.llm import llm_with_tools
from src.email_assistant.prompts.prompts import agent_system_prompt_hitl_memory, GMAIL_TOOLS_PROMPT, default_background, \
    default_cal_preferences, default_response_preferences


def llm_call(state: MainState):
    """LLM decides whether to call a tool or not"""
    print("------------------------------llm_call---------------------------")
    # Search for existing cal_preferences memory
    cal_preferences = get_memory(store, ("email_assistant", "cal_preferences"), default_cal_preferences)

    # Search for existing response_preferences memory
    response_preferences = get_memory(store, ("email_assistant", "response_preferences"), default_response_preferences) # TODO

    response ={
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": agent_system_prompt_hitl_memory.format(
                        tools_prompt=GMAIL_TOOLS_PROMPT,
                        background=default_background,
                        response_preferences=response_preferences,
                        cal_preferences=cal_preferences
                    )}
                ]
                + state["messages"]
            )
        ]
    }
    print(f"llm_call- response:- {response}")
    return response
