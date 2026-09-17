from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from tools.read_file import read_file
from tools.tail_log import tail_log
from tools.search_codebase import search_codebase

llm = ChatOllama(model="qwen3.5-verora")

agent = create_react_agent(
    model=llm,
    tools=[read_file, tail_log, search_codebase]
)


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
