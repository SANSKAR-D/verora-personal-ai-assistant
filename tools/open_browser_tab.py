from tools.pinchtab_manager import get_instance_id, set_tab_id, api_post, api_get, get_tab_id


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
        
        # We always want to bring the new URL to the foreground. 
        # PinchTab's 'navigate' doesn't steal focus, but 'tabs/open' with 'active: True' does.
        # To prevent tab accumulation, we close the previous tab first.
        saved_tab_id = get_tab_id()
        if saved_tab_id:
            try:
                # Silently close the old tab
                api_post(f"/tabs/{saved_tab_id}/close", {})
            except Exception:
                pass

        # Open a new tab and make it active (steals focus)
        resp = api_post(
            f"/instances/{instance_id}/tabs/open",
            {"url": url, "active": True},
        )
        
        tab_id = resp.get("tabId") or resp.get("id")
        if not tab_id:
            return f"Failed to open tab. PinchTab response: {resp}"

        set_tab_id(tab_id)

        # Force visual tab switch if Chrome is the active window
        try:
            import pygetwindow as gw
            import pyautogui
            import time
            
            # Wait a tiny bit for the new tab to spawn
            time.sleep(0.5)
            active_window = gw.getActiveWindow()
            if active_window and 'Chrome' in active_window.title:
                # If they are stuck looking at about:blank, close it to auto-focus the new tab
                if 'about:blank' in active_window.title:
                    pyautogui.hotkey('ctrl', 'w')
                else:
                    # Otherwise just switch to the newly opened tab
                    pyautogui.hotkey('ctrl', 'tab')
        except Exception:
            pass

        return f"Browser navigated to {url}. Ready for get_page_snapshot."

    except Exception as e:
        return f"Failed to open browser tab: {e}"

