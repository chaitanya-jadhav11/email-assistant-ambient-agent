from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from src.email_assistant.graphs.states.state import RouterSchema
from src.email_assistant.tools.base import get_tools

load_dotenv(override=True)

# Initialize the LLM for use with router / structured output
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_router = llm.with_structured_output(RouterSchema)

tools = get_tools(["send_email_tool", "schedule_meeting_tool", "check_calendar_tool", "Question", "Done"], include_gmail=True)
print(f"tools list:-  {tools}")
llm_with_tools = llm.bind_tools(tools, tool_choice="required")
