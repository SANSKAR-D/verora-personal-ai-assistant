from tools.pinchtab_manager import get_tab_id, api_post
from tools.procedural_memory import log_task_attempt, recall_task_history

def browser_action(ref: str, action_type: str, value: str = "", wait_nav: bool = False) -> str:
    """Performs a single action on a specific element identified by its PinchTab ref.

    The ref MUST come from a prior get_page_snapshot call — NEVER guess a ref.

    Supported action types:
    - 'click': Clicks the element (no value needed)
    - 'fill': Types text into an input field (value = the text to type)
    - 'press': Presses a keyboard key on the element (value = key name, e.g. 'Enter')

    Args:
        ref: The element reference from get_page_snapshot (e.g. 'e1', 'e5').
        action_type: One of 'click', 'fill', or 'press'.
        value: The text to type (for 'fill') or key to press (for 'press'). Leave empty for 'click'.
        wait_nav: Set to True if this action is expected to load a new page (e.g., clicking a search button or a link).

    Returns:
        A confirmation message, or an error describing what failed.
    """
    task_name = f"browser_action_{action_type}_ref_{ref}"
    history = recall_task_history(task_name)
    
    try:
        tab_id = get_tab_id()
        if not tab_id:
            msg = "No browser tab is open. Call open_browser_tab first."
            log_task_attempt(task_name, "failure", {"error": msg})
            return msg

        body = {"kind": action_type, "ref": ref}
        if wait_nav:
            body["waitNav"] = True
            
        if action_type == "fill":
            body["value"] = value
        elif action_type == "press":
            body["key"] = value

        resp = api_post(f"/tabs/{tab_id}/action", body)

        if isinstance(resp, dict) and "error" in resp:
            msg = f"Action failed on ref '{ref}': {resp['error']}"
            log_task_attempt(task_name, "failure", {"error": msg, "resp": resp})
            # Also append history warning if we had failures before
            if "No prior attempts found" not in history:
                msg += f"\n\nWarning, you've tried this before:\n{history}"
            return msg

        msg = f"Successfully performed '{action_type}' on element {ref}."
        log_task_attempt(task_name, "success", {"value": value})
        return msg

    except Exception as e:
        msg = f"Browser action failed: {e}"
        log_task_attempt(task_name, "error", {"error": str(e)})
        return msg
