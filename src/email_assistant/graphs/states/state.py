from typing import TypedDict, Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class RouterSchema(BaseModel):
    """Analyze the unread email and route it according to its content."""

    reasoning: str = Field(
        description="Step-by-step reasoning behind the classification."
    )
    classification: Literal["ignore", "respond", "notify"] = Field(
        description="The classification of an email: 'ignore' for irrelevant emails, "
        "'notify' for important information that doesn't need a response, "
        "'respond' for emails that need a reply",
    )



class MainState(MessagesState):
    # This state class has the messages key build in
    email_input: dict
    classification_decision: Literal["ignore", "respond", "notify"]

class StateInput(TypedDict):
    # This is the input to the state
    email_input: dict


from pydantic import BaseModel, Field


class Preferences(BaseModel):
    instructions: str = Field(
        description="User preferences"
    )


class UserPreferences(BaseModel):
    chain_of_thought: str
    user_preferences: Preferences



#class UserPreferences(BaseModel):
#    """Updated user preferences based on user's feedback."""
#    chain_of_thought: str = Field(description="Reasoning about which user preferences need to add/update if required")
#    user_preferences: str = Field(description="Updated user preferences")