import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store
from agent.overlay import signals

def confirm_action(description: str) -> bool:
    """Shows the proposed action and waits for explicit user approval."""
    store.update("is_confirming", True)
    store.update("confirmation_result", None)
    
    print(f"\n======================================")
    print(f"[CONFIRMATION NEEDED]")
    print(f"{description}")
    print(f"======================================\n")
    
    signals.prompt_signal.emit(description)
    
    while store.get("confirmation_result") is None:
        time.sleep(0.1)
        
    result = store.get("confirmation_result")
    
    store.update("is_confirming", False)
    return result
