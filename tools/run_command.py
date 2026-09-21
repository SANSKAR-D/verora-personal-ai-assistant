import subprocess
from agent.confirmation import confirm_action

def run_command(command: str) -> str:
    """Executes a Windows shell command, with user confirmation first.
    This is ONLY for terminal commands like 'dir', 'mkdir', 'tasklist', 'taskkill'.
    DO NOT use this for browsing the web — use open_browser_tab instead.
    This system runs Windows, NOT Linux. Do NOT use Linux commands like grep, fuser, env, cat, ls."""
    
    # Block browser/URL commands
    forbidden_url_terms = ["http://", "https://", "www.", "xdg-open", "google-chrome", "firefox", "msedge"]
    if any(term in command.lower() for term in forbidden_url_terms):
        return "ERROR: You are forbidden from using run_command to open websites. Use open_browser_tab instead."
    
    # Block Linux commands — this is Windows!
    linux_commands = ["grep", "fuser", "env ", "cat ", "ls ", "chmod", "chown", "sudo", "apt", "wget", "curl"]
    if any(command.lower().strip().startswith(cmd) or f" {cmd}" in command.lower() for cmd in linux_commands):
        return "ERROR: This is a Windows system. Linux commands like grep/fuser/env do not work here. Use Windows equivalents (findstr, tasklist, set, dir, type)."
        
    if not confirm_action(f"Run command: {command}"):
        return "Command cancelled by user."

    try:
        result = subprocess.run(command, shell=True, capture_output=True, timeout=30, text=True)
        return result.stdout or result.stderr or "Command completed with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Command failed: {e}"
