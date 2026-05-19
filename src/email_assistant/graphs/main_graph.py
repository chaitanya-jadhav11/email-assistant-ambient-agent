# Build overall workflow with store and checkpointer
import random
from pathlib import Path

from dotenv import load_dotenv
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.email_assistant.db.db import checkpointer, init_db
from src.email_assistant.graphs.nodes.interrupt_handler import interrupt_handler
from src.email_assistant.graphs.nodes.llm_call import llm_call
from src.email_assistant.graphs.nodes.mark_as_read import mark_as_read_node
from src.email_assistant.graphs.nodes.triage_interrupt_handler import triage_interrupt_handler
from src.email_assistant.graphs.nodes.triage_router import triage_router
from src.email_assistant.graphs.routers.should_continue import should_continue
from src.email_assistant.graphs.states.state import StateInput, MainState

load_dotenv(override=True)

# Add nodes - with store parameter
agent_builder = StateGraph(MainState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("interrupt_handler", interrupt_handler)
agent_builder.add_node("mark_as_read_node", mark_as_read_node)

# Add edges
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "interrupt_handler": "interrupt_handler",
        "mark_as_read_node": "mark_as_read_node",
    },
)
agent_builder.add_edge("mark_as_read_node", END)

# Compile the agent
response_agent = agent_builder.compile()


response_agent.get_graph(xray=1).print_ascii()
response_agent.get_graph(xray=1).draw_mermaid_png(
    output_file_path="src/graph_flow_diagram/response_agent.png")


# Build overall workflow with store and checkpointer
overall_workflow = (
    StateGraph(MainState, input=StateInput)
    .add_node(triage_router)
    .add_node(triage_interrupt_handler)
    .add_node("response_agent", response_agent)
    #.add_node("mark_as_read_node", mark_as_read_node)

    .add_edge(START, "triage_router")
    #.add_edge("mark_as_read_node", END)
)
# Compile Outer Graph
#email_assistant_graph = overall_workflow.compile(checkpointer=checkpointer) # checkpointer not worked with langgraph dev
email_assistant_graph = overall_workflow.compile()


email_assistant_graph.get_graph(xray=1).print_ascii()
email_assistant_graph.get_graph(xray=1).draw_mermaid_png(
    output_file_path="src/graph_flow_diagram/" + Path(__file__).stem + ".png")

def main ():
   print("hi")
   # notify....
   email_input1 = {
       "from": "",
       "body": "triage_interrupt_handler",
       "id": "11",
       "author": "System Admin <sysadmin@company.com>",
       "to": "Development Team <dev@company.com>",
       "subject": "Scheduled maintenance - database downtime",
       "email_thread": "Hi team,\n\nThis is a reminder that we'll be performing scheduled maintenance on the production database tonight from 2AM to 4AM EST. During this time, all database services will be unavailable.\n\nPlease plan your work accordingly and ensure no critical deployments are scheduled during this window.\n\nThanks,\nSystem Admin Team"
   }
   # ignore....
   email_input1 = {
       "from": "",
       "body": "triage_interrupt_handler",
       "id": "13",
       "author": "Crypto Rewards <claim@free-bitcoin-now.net>",
       "to": "Development Team <dev@company.com>",
       "subject": "URGENT: You won 2.5 BTC reward!!!",
       "email_thread": "Congratulations!!!\n\nYour email was randomly selected to receive 2.5 Bitcoin as part of our international crypto giveaway.\n\nClick the link below within 24 hours to claim your reward:\nhttp://free-bitcoin-now.net/claim\n\nFailure to respond will result in permanent cancellation of your reward.\n\nBest Regards,\nCrypto Rewards Team"
   }
   email_input = {
       "from": "",
       "body": "triage_interrupt_handler",
       "id": "14",
       "author": "Sarah Johnson <sarah.johnson@clientcorp.com>",
       "to": "Development Team <dev@company.com>",
       "subject": "Need update on API integration timeline",
       "email_thread": "Hi team,\n\nWe are planning our production rollout next week and wanted to check the current status of the payment API integration.\n\nCould you please share:\n- Expected completion date\n- Any blockers remaining\n- Whether sandbox testing is complete\n\nPlease let us know by today evening so we can finalize our deployment schedule.\n\nThanks,\nSarah"
   }

   email_input1 = {
       "goto": "triage_interrupt_handler"
   }
   # Run the agent

   # Your original configuration
   config = {"configurable": {"thread_id": "1"}}

   # Generate a random integer (for example, between 1 and 100)
   random_num = random.randint(1, 1000000)

   # Add it to the nested "configurable" dictionary
   config["configurable"]["thread_id"] = random_num

   response = email_assistant_graph.invoke({"email_input": email_input},config= config)
   print(f"Response {response} ")

   for m in response["messages"]:
       m.pretty_print()




# uv run -m src.email_assistant.graphs.main_graph
if __name__ == "__main__":
    main()