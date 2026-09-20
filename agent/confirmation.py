import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

def confirm_action(description: str) -> bool:
    """Shows the proposed action and waits for explicit user approval."""
    store.update("is_confirming", True)
    
    print(f"\n======================================")
    print(f"[CONFIRMATION NEEDED]")
    print(f"{description}")
    print(f"======================================\n")
    
    response = input("Verora wants permission to proceed. (yes/no): ").strip().lower()
    
    store.update("is_confirming", False)
    return response in ("yes", "y")
