import json

from langchain.chat_models import init_chat_model

from src.email_assistant.graphs.states.state import UserPreferences
from src.email_assistant.prompts.prompts import MEMORY_UPDATE_INSTRUCTIONS


def get_memory(store, namespace, default_content=""):
    """Get memory from the store or initialize with default if it doesn't exist.

    Args:
        store: LangGraph BaseStore instance to search for existing memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        default_content: Default content to use if memory doesn't exist

    Returns:
        str: The content of the memory profile, either from existing memory or the default
    """
    # Search for existing memory with namespace and key
    user_preferences = store.get(namespace, "user_preferences")

    # If memory exists, return its content (the value)
    if user_preferences:
        return user_preferences.value

    # If memory doesn't exist, add it to the store and return the default content
    else:
        # Namespace, key, value
        import json

        # Your Python object (dictionary)
        data = {
            "instructions": default_content
        }
        # Create a JSON string
        json_string = json.dumps(data)

        print(json_string)


        store.put(namespace, "user_preferences", json_string)
        user_preferences = default_content

    # Return the default content
    return user_preferences


def update_memory(store, namespace, messages):
    """Update memory profile in the store.

    Args:
        store: LangGraph BaseStore instance to update memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        messages: List of messages to update the memory with
    """

    # Get the existing memory
    user_preferences = store.get(namespace, "user_preferences")
    # Update the memory
    llm = init_chat_model("openai:gpt-4.1", temperature=0.0).with_structured_output(UserPreferences)
    result = llm.invoke(
        [
            {"role": "system",
             "content": MEMORY_UPDATE_INSTRUCTIONS.format(current_profile=user_preferences.value, namespace=namespace)},
        ] + messages
    )
    print(f"Updated memory:- {result}")
    # Save the updated memory to the store

    # Your Python object (dictionary)
    data = {
        "instructions": result.user_preferences.instructions
    }
    # Create a JSON string
    json_string = json.dumps(data)

    print(json_string)



    store.put(namespace, "user_preferences", json_string)