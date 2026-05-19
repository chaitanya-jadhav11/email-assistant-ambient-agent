from src.email_assistant.db.db import store


# =========================================================
# 1. CREATE DATA
# =========================================================
def create_user_memory(user_id: str, key: str, data: dict):
    """
    Create new memory in LangGraph Store.

    Args:
        user_id: Namespace / user identifier
        key: Unique memory key
        data: Dictionary payload
    """

    namespace = ("users", user_id)
    print(f"namespace type: {type(namespace)}")

    store.put(
        namespace,
        key,
        data
    )

    print(f"Created memory: {key}")


# =========================================================
# 2. UPDATE DATA
# =========================================================
def update_user_memory(user_id: str, key: str, updated_data: dict):
    """
    Update existing memory.

    NOTE:
    put() overwrites existing value for same key.
    """

    namespace = ("users", user_id)

    existing = store.get(namespace, key)

    if not existing:
        print("Memory not found")
        return

    # Merge old + new
    merged_data = {
        **existing.value,
        **updated_data
    }

    store.put(
        namespace,
        key,
        merged_data
    )

    print(f"Updated memory: {key}")

def get_user_memory(user_id: str, key: str):
    namespace = ("users", user_id)
    existing = store.get(namespace, key)
    print(f" get memory {existing}")


# =========================================================
# 3. ADD DATA TO EXISTING LIST
# =========================================================
def add_message_to_memory(user_id: str, key: str, new_message: str):
    """
    Add item into existing messages list.

    Example structure:
    {
        "messages": ["hello", "hi"]
    }
    """

    namespace = ("users", user_id)

    existing = store.get(namespace,  key)

    if not existing:
        print("Memory not found")
        return

    data = existing.value

    # Create messages list if missing
    if "messages" not in data:
        data["messages"] = []

    data["messages"].append(new_message)

    store.put(
        namespace,
        key,
        data
    )

    print(f"Added message to memory: {key}")

#  uv run -m src.email_assistant.db.db_test
def main():
    create_user_memory(user_id="user_2", key="my_key_2", data={"id":"4"})

    update_user_memory(
        user_id="user_2",
        key="my_key_2",
        updated_data={
            "role": "Senior AI Engineer",
            "city": "Pune"
        }
    )
    # Add Data to Existing List----------------------
    create_user_memory(
        user_id="user_3",
        key="chat_memory",
        data={
            "messages": []
        }
    )
    add_message_to_memory(
        user_id="user_3",
        key="chat_memory",
        new_message="Hello"
    )
    add_message_to_memory(
        user_id="user_2",
        key="chat_memory",
        new_message="How are you?"
    )

    #-----------------------------------------------------------

    get_user_memory(user_id="user_2", key="my_key_2")


if __name__ == "__main__":
    # main()
    get_user_memory(user_id="user_2", key="my_key_2")