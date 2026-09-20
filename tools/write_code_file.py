import os
from agent.confirmation import confirm_action

def write_code_file(filepath: str, content: str) -> str:
    """Writes content to a code file in the project, with confirmation."""
    preview = content[:300] + "..." if len(content) > 300 else content
    
    if not confirm_action(f"Write to file: {filepath}\n\nContent preview:\n{preview}"):
        return "File write cancelled by user."

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {len(content)} characters to {filepath}"
    except Exception as e:
        return f"Failed to write file: {e}"
