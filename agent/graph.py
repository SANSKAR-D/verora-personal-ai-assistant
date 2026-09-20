from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama

# Import tools
from tools.read_file import read_file
from tools.tail_log import tail_log
from tools.search_codebase import search_codebase
from tools.capture_and_read_screen import capture_and_read_screen
from tools.close_overlay import close_overlay
from tools.open_app import open_app
from tools.run_command import run_command
from tools.send_message import send_message
from tools.write_code_file import write_code_file

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(model="qwen3.5-verora")

# --- TOOLS ---
READ_ONLY_TOOLS = [read_file, tail_log, search_codebase, capture_and_read_screen, close_overlay,open_app]
CONFIRMATION_TOOLS = [run_command, send_message, write_code_file]

all_tools = READ_ONLY_TOOLS + CONFIRMATION_TOOLS
llm_with_tools = llm.bind_tools(all_tools)
tool_node = ToolNode(all_tools)

# --- GRAPH NODES ---
def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END

# --- COMPILE ---
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

# Compile WITHOUT MemorySaver so our ask_with_pruning function still controls history!
agent = graph.compile()

# --- NEW: Context Pruning Wrapper ---
def ask_with_pruning(question: str, history: list = None, max_history: int = 10):
    """
    Passes the question to the agent while dropping old context 
    to prevent prompt-size bloat during long sessions.
    """
    history = history or []
    # keep only the last N messages
    trimmed_history = history[-max_history:]  
    messages = trimmed_history + [{"role": "user", "content": question}]
    
    # Invoke the agent
    result = agent.invoke({"messages": messages})
    
    # Return the new history and the final answer
    return result["messages"], result["messages"][-1].content
