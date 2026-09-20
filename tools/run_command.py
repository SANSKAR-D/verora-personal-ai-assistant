import subprocess
from agent.confirmation import confirm_action

def run_command(command: str) -> str:
    """Executes a shell command, with user confirmation first."""
    forbidden_terms = ["http://", "https://", "www.", "xdg-open", "google-chrome", "firefox", "msedge"]
    if any(term in command.lower() for term in forbidden_terms):
        return "ERROR: You are strictly forbidden from using run_command to open websites or browsers. You MUST use the `automate_browser` tool!"
        
    if not confirm_action(f"Run command: {command}"):
        return "Command cancelled by user."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=30, text=True)
        return result.stdout or result.stderr or "Command completed with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Command failed: {e}"
