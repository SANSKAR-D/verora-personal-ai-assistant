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

# PinchTab browser tools (replaces Playwright)
from tools.open_browser_tab import open_browser_tab
from tools.get_page_snapshot import get_page_snapshot
from tools.browser_action import browser_action
from tools.web_search import web_search
from tools.crawl_page import crawl_page
from tools.extract_from_page import extract_from_page
from tools.crawl_docs import crawl_docs
from tools.memory_semantic import save_memory, recall_memory
from tools.memory_episodic import log_episode, recall_episodes
from tools.memory_entity import upsert_entity, query_entity
from tools.tasks_and_calendar import add_task, list_tasks, complete_task



class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(model="qwen3.5-verora")

# --- TOOLS ---
#capture_and_read_screen,run_command
READ_ONLY_TOOLS = [
    read_file, tail_log, search_codebase, close_overlay, open_app,
    update_scratchpad,capture_and_read_screen,
    web_search, crawl_page, extract_from_page,
    # PinchTab browser tools — no confirmation needed for these
    open_browser_tab, get_page_snapshot, browser_action,
    # New memory tools
    save_memory, recall_memory, log_episode, recall_episodes,
    upsert_entity, query_entity, add_task, list_tasks, complete_task
]
CONFIRMATION_TOOLS = [send_message, write_code_file, login_to_site,run_command,crawl_docs]

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
    # Keep only the last N messages (strictly limit the number of messages to prevent bloat)
    trimmed_history = history[-max_history:]
    
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
        "WEB SEARCH & PAGE READING\n"
        "==================================================\n"
        "When you need up-to-date information or facts from the internet, use these tools IN THIS ORDER OF PREFERENCE:\n\n"
        "1. web_search(query) — Search the live web. Use this FIRST for any question needing current info.\n"
        "   Example: web_search(query='latest Python version 2026')\n\n"
        "2. crawl_page(url) — Fetch and read a specific URL. Use this to read articles, docs, or pages.\n"
        "   Example: crawl_page(url='https://pytorch.org/docs/stable/torch.compile.html')\n\n"
        "3. extract_from_page(url, question) — Use the LLM to extract a SPECIFIC answer from a URL.\n"
        "   Only use this when crawl_page returns too much text or too little useful content.\n"
        "   Example: extract_from_page(url='https://docs.python.org/3/whatsnew.html', question='What is new in Python 3.13?')\n\n"
        "4. crawl_docs(urls, question) — Extract answers spanning MULTIPLE pages. Requires confirmation.\n\n"
        
        "CRITICAL RESPONSE FORMAT: You MUST keep spoken responses extremely short.\n"
        "If your answer is long, put a 1-2 sentence summary inside <speak>...</speak> tags. ONLY the text inside these tags will be spoken aloud.\n"
        "Put the full detailed information OUTSIDE the tags (it will be displayed silently on a translucent black screen).\n"
        "Example: <speak>I found the weather for New York.</speak> The current temp is 75F, sunny, humidity 45%...\n\n"

        "CRITICAL: Do NOT answer questions about current events, versions, or live data from memory alone.\n"
        "          ALWAYS use web_search or crawl_page to ground your answer in real, fresh data.\n\n"

        "==================================================\n"
        "OTHER TOOL GUIDELINES\n"
        "==================================================\n"
        "- To run terminal commands (dir, mkdir, taskkill): use run_command. NEVER for URLs.\n"
        "- To open native apps (notepad, calc): use open_app. NEVER for websites.\n"
        "- To log into a site: use login_to_site(login_url, site_name)\n"
        "  Example: login_to_site(login_url='https://github.com/login', site_name='github')\n"
        "- To save important facts permanently: use save_memory(fact). To retrieve them, use recall_memory(query).\n"
        "- To track your current task progress: use update_scratchpad(status)\n\n"

        "==================================================\n"
        "CURRENT TASK SCRATCHPAD\n"
        "==================================================\n"
        "This is your current task list. Use 'update_scratchpad' to update it mid-task:\n"
        f"{current_scratchpad}"
    )
    
    # Inject the system prompt with memory and task scratchpad
    system_prompt = {"role": "system", "content": system_instruction}
    messages = [system_prompt] + trimmed_history + [{"role": "user", "content": question}]
    
    from agent.overlay import signals
    
    # Invoke the agent via stream to show live status
    final_messages = None
    for event in agent.stream({"messages": messages}, stream_mode="values"):
        final_messages = event["messages"]
        last_msg = final_messages[-1]
        
        if last_msg.type == "ai":
            if getattr(last_msg, "tool_calls", None):
                tool_names = ", ".join([tc["name"] for tc in last_msg.tool_calls])
                signals.update_signal.emit(f"Using {tool_names}...")
            else:
                signals.update_signal.emit("Thinking...")
        elif last_msg.type == "tool":
            signals.update_signal.emit("Processing results...")
            
    # Find the final AI text response (walk backwards past tool messages)
    import re
    final_answer = ""
    for msg in reversed(final_messages):
        if msg.type == "ai" and msg.content:
            raw = msg.content
            print(f"[Graph] Raw AI message content: {raw[:500]}")
            
            # Strip Qwen3 <think> reasoning (REMOVE — this is internal thought)
            raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL)
            # Handle unclosed <think> tag (model was cut off mid-thought)
            raw = re.sub(r'<think>.*', '', raw, flags=re.DOTALL)
            
            # Strip special tokens like <|im_end|>
            raw = re.sub(r'<\|.*?\|>', '', raw)
            raw = raw.strip()
            
            if raw:
                final_answer = raw
                break
    
    print(f"[Graph] Final answer extracted ({len(final_answer)} chars): {final_answer[:300]}")
    return final_messages, final_answer
