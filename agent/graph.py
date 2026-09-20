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
from tools.login_to_site import login_to_site
from tools.update_scratchpad import update_scratchpad
from tools.update_memory import update_memory
from tools.automate_browser import automate_browser
from tools.play_youtube import play_youtube



class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(model="qwen3.5-verora")

# --- TOOLS ---
READ_ONLY_TOOLS = [read_file, tail_log, play_youtube,search_codebase, capture_and_read_screen, close_overlay,open_app, automate_browser, update_memory, update_scratchpad]
CONFIRMATION_TOOLS = [run_command, send_message, write_code_file, login_to_site]

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
    
    # Read her permanent long-term memory
    try:
        with open("long_term_memory.txt", "r", encoding="utf-8") as f:
            permanent_memory = f.read().strip()
    except Exception:
        permanent_memory = "No memories yet."
        
    # Read her short-term task scratchpad
    try:
        with open("scratchpad.txt", "r", encoding="utf-8") as f:
            current_scratchpad = f.read().strip()
    except Exception:
        current_scratchpad = "No current tasks."
        
    system_instruction = (
        "You are Verora, a highly capable AI assistant. You MUST process all input as English, and you MUST ONLY reply in English. Never use Hindi.\n\n"
        "==================================================\n"
        "CRITICAL TOOL USAGE GUIDELINES & EXAMPLES\n"
        "==================================================\n"
        "You have several tools. YOU MUST USE THEM CORRECTLY based on the task:\n\n"
        
        "1. WEB BROWSING & AUTOMATION (automate_browser)\n"
        "If the user asks you to search Wikipedia, Google something, or browse ANY website, you MUST use the `automate_browser` tool.\n"
        "DO NOT use `run_command` (like xdg-open or google-chrome) to open URLs. You are strictly forbidden from doing that.\n"
        "The `automate_browser` tool requires two arguments: `url` and a list of `actions`.\n"
        "Example 1: Searching Wikipedia\n"
        "  - url: 'https://en.wikipedia.org'\n"
        "  - actions: [\n"
        "      {\"type\": \"type\", \"selector\": \"input[type='search']\", \"text\": \"Python programming\"},\n"
        "      {\"type\": \"press\", \"selector\": \"input[type='search']\", \"key\": \"Enter\"}\n"
        "    ]\n"
        "Example 2: Searching Google\n"
        "  - url: 'https://www.google.com'\n"
        "  - actions: [\n"
        "      {\"type\": \"type\", \"selector\": \"textarea[name='q']\", \"text\": \"Weather today\"},\n"
        "      {\"type\": \"press\", \"selector\": \"textarea[name='q']\", \"key\": \"Enter\"}\n"
        "    ]\n"
        "Example 3: Just opening a webpage (no actions needed)\n"
        "  - url: 'https://en.wikipedia.org/wiki/Python_(programming_language)'\n"
        "  - actions: []\n"
        "Example 4: Interacting with the ALREADY OPEN webpage (e.g. clicking 'Donate' on Wikipedia)\n"
        "  - url: ''\n"
        "  - actions: [\n"
        "      {\"type\": \"click\", \"selector\": \"a:has-text('Donate')\"}\n"
        "    ]\n\n"
        
        "2. YOUTUBE MUSIC (play_youtube)\n"
        "If the user asks to play a song on YouTube, strictly use the `play_youtube` tool with the song name.\n\n"
        
        "3. RUNNING COMMANDS (run_command)\n"
        "Use `run_command` strictly for terminal/bash commands like 'dir', 'mkdir', 'taskkill'.\n"
        "NEVER use run_command for opening web browsers or URLs.\n\n"
        
        "==================================================\n"
        "PERMANENT LONG-TERM MEMORY\n"
        "==================================================\n"
        "Here are facts and lessons you have learned in the past. NEVER FORGET THESE:\n"
        f"{permanent_memory}\n\n"
        "==================================================\n"
        "CURRENT TASK SCRATCHPAD\n"
        "==================================================\n"
        "This is your current task list. Use 'update_scratchpad' to update it mid-task:\n"
        f"{current_scratchpad}"
    )
    
    # Inject a strict System Prompt forcing her to only process and speak in English, plus her memory!
    system_prompt = {"role": "system", "content": system_instruction}
    messages = [system_prompt] + trimmed_history + [{"role": "user", "content": question}]
    
    # Invoke the agent
    result = agent.invoke({"messages": messages})
    
    # Return the new history and the final answer
    return result["messages"], result["messages"][-1].content
