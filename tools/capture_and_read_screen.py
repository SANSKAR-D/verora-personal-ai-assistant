from tools.capture_screen import capture_active_window
from tools.understand_screen import understand_screen

def capture_and_read_screen(question: str = "What does this show?") -> str:
    """Takes a screenshot of the active desktop window and describes its visual content.
    Use this ONLY when the user explicitly asks 'what is on my screen' or 'read my screen'.
    DO NOT use this for browser automation — use open_browser_tab + get_page_snapshot instead.
    DO NOT use this as a first step before browsing the web."""
    path = capture_active_window()
    return understand_screen(path, question)
