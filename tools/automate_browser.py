import time
from playwright.sync_api import sync_playwright

# Global variables to keep the browser open!
_p = None
_browser = None

def get_page():
    global _p, _browser
    if _p is None:
        _p = sync_playwright().start()
    if _browser is None or not _browser.is_connected():
        _browser = _p.chromium.launch(headless=False, slow_mo=500)
        
    contexts = _browser.contexts
    if not contexts:
        context = _browser.new_context()
    else:
        context = contexts[0]
        
    pages = context.pages
    if not pages:
        page = context.new_page()
    else:
        page = pages[-1] # Reuse the currently active tab!
        
    return page

def automate_browser(url: str, actions: list[dict]) -> str:
    """
    Control a visible web browser to perform generic tasks!
    'actions' is a list of dictionaries.
    Supported types:
    - "click": requires "selector" (CSS or text like "button:has-text('Search')")
    - "type": requires "selector" and "text"
    - "press": requires "selector" and "key" (e.g., "Enter")
    """
    try:
        page = get_page()
        
        # Only navigate if a URL was actually provided!
        if url and url.strip() != "":
            page.goto(url)
        
        # Execute the list of actions
        for action in actions:
            selector = action["selector"]
            
            try:
                # Increased timeout to 15 seconds! Webpages can take a bit to fully render the buttons.
                if action["type"] == "click":
                    page.locator(selector).first.click(timeout=15000)
                elif action["type"] == "type":
                    page.locator(selector).first.fill(action["text"], timeout=15000)
                elif action["type"] == "press":
                    page.locator(selector).first.press(action["key"], timeout=15000)
            except Exception as inner_e:
                return f"Action {action} failed on selector '{selector}'. Error: {inner_e}"
                
        # We no longer close the browser! It stays open for the user!
        return f"Successfully completed {len(actions)} actions on {url}!"
        
    except Exception as e:
        return f"Browser automation failed: {e}"
