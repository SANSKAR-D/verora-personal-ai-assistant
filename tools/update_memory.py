import os

MEMORY_FILE = "long_term_memory.txt"

def update_memory(new_information: str) -> str:
    """
    Appends a new fact, rule, or lesson learned to your permanent long-term memory.
    Use this to remember mistakes you made with Playwright so you never repeat them!
    Example: update_memory("The GitHub username field uses id='login_field'")
    """
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"- {new_information}\n")
        return "Successfully committed to long-term memory! I will never forget this."
    except Exception as e:
        return f"Failed to update memory: {e}"
