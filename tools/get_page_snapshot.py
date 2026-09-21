from tools.pinchtab_manager import get_tab_id, api_get


def get_page_snapshot() -> str:
    """Returns the current page's interactive elements (buttons, links, input fields)
    with their stable reference IDs (e.g. 'e1', 'e5', 'e12').

    ALWAYS call this before attempting to click or fill anything on a page.
    NEVER guess an element reference — read the snapshot first.

    Use this immediately after calling open_browser_tab, or when the page has changed
    and you need to see the updated elements.

    Returns:
        A list of interactive elements with their refs, roles, and visible labels.
        Example: 'e3:search "Search Wikipedia" | e7:link "Donate" | e9:link "Log in"'
    """
    try:
        tab_id = get_tab_id()
        if not tab_id:
            return "No browser tab is open. Call open_browser_tab first."

        data = api_get(f"/tabs/{tab_id}/snapshot", params={"filter": "interactive"})

        if isinstance(data, dict) and "error" in data:
            return f"Snapshot failed: {data['error']}"

        # PinchTab returns {"count": N, "nodes": [...]}
        nodes = []
        if isinstance(data, dict) and "nodes" in data:
            nodes = data["nodes"]
        elif isinstance(data, list):
            nodes = data

        if not nodes:
            return "No interactive elements found on this page."

        # Format into a clean, readable list for the LLM
        lines = []
        for elem in nodes:
            ref = elem.get("ref", "?")
            role = elem.get("role", "unknown")
            name = elem.get("name", "") or elem.get("text", "")
            lines.append(f"{ref}:{role} \"{name}\"")

        return "\n".join(lines)

    except Exception as e:
        return f"Failed to get page snapshot: {e}"
