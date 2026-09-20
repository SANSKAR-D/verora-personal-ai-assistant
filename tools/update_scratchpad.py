import os

SCRATCHPAD_FILE = "scratchpad.txt"

def update_scratchpad(current_task_status: str) -> str:
    """
    Updates your short-term scratchpad.
    Use this to write down your current plan or task list so you don't lose track of what you are doing mid-task.
    This overwrites the previous scratchpad contents.
    Example: update_scratchpad("1. Search Wikipedia (Done) 2. Click Donate (Pending)")
    """
    try:
        with open(SCRATCHPAD_FILE, "w", encoding="utf-8") as f:
            f.write(current_task_status)
        return "Scratchpad updated successfully."
    except Exception as e:
        return f"Failed to update scratchpad: {e}"
