import subprocess
from agent.confirmation import confirm_action

def run_command(command: str) -> str:
    """Executes a shell command, with user confirmation first."""
    if not confirm_action(f"Run command: {command}"):
        return "Command cancelled by user."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=30, text=True)
        return result.stdout or result.stderr or "Command completed with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Command failed: {e}"
