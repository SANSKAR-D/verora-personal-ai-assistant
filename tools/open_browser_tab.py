from tools.pinchtab_manager import get_instance_id, set_tab_id, api_post


def open_browser_tab(url: str) -> str:
    """Opens a new headed (visible) browser tab at the given URL using PinchTab,
    and stores the tab ID for subsequent get_page_snapshot and browser_action calls.

    Use this as the FIRST step for any browser task. Always follow it with
    get_page_snapshot before attempting any interaction on the page.

    DO NOT use run_command or open_app for websites. Use this tool instead.

    Args:
        url: The web address to open (e.g. 'https://en.wikipedia.org').

    Returns:
        A confirmation message with the tab ID ready for follow-up calls.
    """
    try:
        instance_id = get_instance_id()
        resp = api_post(
            f"/instances/{instance_id}/tabs/open",
            {"url": url},
        )
        tab_id = resp.get("tabId") or resp.get("id")
        if not tab_id:
            return f"Failed to open tab. PinchTab response: {resp}"

        set_tab_id(tab_id)
        return f"Browser tab opened at {url}. Ready for get_page_snapshot."

    except Exception as e:
        return f"Failed to open browser tab: {e}"
