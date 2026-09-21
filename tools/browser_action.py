from tools.pinchtab_manager import get_tab_id, api_post


def browser_action(ref: str, action_type: str, value: str = "") -> str:
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

    Returns:
        A confirmation message, or an error describing what failed.
    """
    try:
        tab_id = get_tab_id()
        if not tab_id:
            return "No browser tab is open. Call open_browser_tab first."

        body = {"kind": action_type, "ref": ref}
        if action_type == "fill":
            body["value"] = value
        elif action_type == "press":
            body["key"] = value

        resp = api_post(f"/tabs/{tab_id}/action", body)

        if isinstance(resp, dict) and "error" in resp:
            return f"Action failed on ref '{ref}': {resp['error']}"

        return f"Successfully performed '{action_type}' on element {ref}."

    except Exception as e:
        return f"Browser action failed: {e}"
