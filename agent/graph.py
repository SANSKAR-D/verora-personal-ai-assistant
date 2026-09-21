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

# PinchTab browser tools (replaces Playwright)
from tools.open_browser_tab import open_browser_tab
from tools.get_page_snapshot import get_page_snapshot
from tools.browser_action import browser_action



class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(model="qwen3.5-verora")

# --- TOOLS ---
#capture_and_read_screen,run_command
READ_ONLY_TOOLS = [
    read_file, tail_log, search_codebase, close_overlay, open_app,
    update_memory, update_scratchpad,capture_and_read_screen,
    # PinchTab browser tools — no confirmation needed for these
    open_browser_tab, get_page_snapshot, browser_action,
]
CONFIRMATION_TOOLS = [send_message, write_code_file, login_to_site,run_command]

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
        "You are Verora, a highly capable AI assistant running on WINDOWS (not Linux). You MUST process all input as English, and you MUST ONLY reply in English. Never use Hindi.\n"
        "You run on Windows — NEVER use Linux commands (grep, fuser, env, cat, ls). Use Windows equivalents (findstr, tasklist, set, dir, type).\n\n"

        "==================================================\n"
        "BROWSER AUTOMATION (PinchTab — 3-step workflow)\n"
        "==================================================\n"
        "For ANY web browsing task (Wikipedia, Google, any website), you MUST follow this exact 3-step pattern:\n\n"

        "STEP 1: Call open_browser_tab(url) to navigate to the page.\n"
        "  Example: open_browser_tab(url='https://en.wikipedia.org')\n\n"

        "STEP 2: Call get_page_snapshot() to see what elements exist on the page.\n"
        "  This returns a list of interactive elements with stable refs like:\n"
        "    e1:search \"Search Wikipedia\"\n"
        "    e7:link \"Donate\"\n"
        "    e9:link \"Log in\"\n\n"

        "STEP 3: Call browser_action(ref, action_type, value) to interact with a specific element.\n"
        "  Examples:\n"
        "    browser_action(ref='e1', action_type='fill', value='Dragon')\n"
        "    browser_action(ref='e2', action_type='click')\n"
        "    browser_action(ref='e1', action_type='press', value='Enter')\n\n"

        "CRITICAL RULES:\n"
        "- NEVER guess a ref. ALWAYS call get_page_snapshot first to see the real refs.\n"
        "- NEVER use run_command to open websites (like xdg-open or google-chrome). You are FORBIDDEN.\n"
        "- NEVER use open_app for websites. open_app is ONLY for native desktop apps like notepad.\n"
        "- If the page changes after an action (e.g. after clicking a link), call get_page_snapshot again to see the new elements.\n"
        "- To interact with an ALREADY OPEN page, just call get_page_snapshot() (no need for open_browser_tab).\n\n"

        "FULL EXAMPLE — Searching Wikipedia for 'Dragon':\n"
        "  1. open_browser_tab(url='https://en.wikipedia.org')\n"
        "  2. get_page_snapshot()  →  sees e1:search \"Search Wikipedia\"\n"
        "  3. browser_action(ref='e1', action_type='fill', value='Dragon')\n"
        "  4. browser_action(ref='e1', action_type='press', value='Enter')\n\n"

        "==================================================\n"
        "OTHER TOOL GUIDELINES\n"
        "==================================================\n"
        "- To play a song on YouTube: use play_youtube(song_name)\n"
        "- To run terminal commands (dir, mkdir, taskkill): use run_command. NEVER for URLs.\n"
        "- To open native apps (notepad, calc): use open_app. NEVER for websites.\n"
        "- To log into a site: use login_to_site(login_url, site_name)\n"
        "  Example: login_to_site(login_url='https://github.com/login', site_name='github')\n"
        "- To save important facts permanently: use update_memory(fact)\n"
        "- To track your current task progress: use update_scratchpad(status)\n\n"

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
    
    # Inject the system prompt with memory and task scratchpad
    system_prompt = {"role": "system", "content": system_instruction}
    messages = [system_prompt] + trimmed_history + [{"role": "user", "content": question}]
    
    # Invoke the agent
    result = agent.invoke({"messages": messages})
    
    # Return the new history and the final answer
    return result["messages"], result["messages"][-1].content
