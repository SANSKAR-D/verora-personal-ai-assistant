from tools.capture_screen import capture_active_window
from tools.understand_screen import understand_screen

def capture_and_read_screen(question: str = "What does this show?") -> str:
    """Takes a screenshot of the active window and describes/reads its content."""
    path = capture_active_window()
    return understand_screen(path, question)
