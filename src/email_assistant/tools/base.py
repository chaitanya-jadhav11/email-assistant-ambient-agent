from typing import Dict, List, Callable, Any, Optional
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel

from src.email_assistant.tools.gmail.gmail_tools import(
    fetch_emails_tool,
    send_email_tool,
    check_calendar_tool,
    schedule_meeting_tool
)


def get_tools(tool_names: Optional[List[str]] = None, include_gmail: bool = False) -> List[BaseTool]:
    """Get specified tools or all tools if tool_names is None.

    Args:
        tool_names: Optional list of tool names to include. If None, returns all tools.
        include_gmail: Whether to include Gmail tools. Defaults to False.

    Returns:
        List of tool objects
    """

    # Add Gmail tools if requested
    try:

        all_tools = {
            "fetch_emails_tool": fetch_emails_tool,
            "send_email_tool": send_email_tool,
            "check_calendar_tool": check_calendar_tool,
            "schedule_meeting_tool": schedule_meeting_tool,
            "Done": Done,
            "Question": Question,
        }
    except ImportError:
        # If Gmail tools aren't available, continue without them
        pass

    if tool_names is None:
        return list(all_tools.values())

    return [all_tools[name] for name in tool_names if name in all_tools]


def get_tools_by_name(tools: Optional[List[BaseTool]] = None) -> Dict[str, BaseTool]:
    """Get a dictionary of tools mapped by name."""
    if tools is None:
        tools = get_tools()

    return {tool.name: tool for tool in tools}

@tool
class Done(BaseModel):
    """E-mail has been sent."""
    done: bool

@tool
class Question(BaseModel):
      """Question to ask user."""
      content: str

