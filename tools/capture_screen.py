import mss
import pygetwindow as gw
from PIL import Image
import os
import uuid

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "temp_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture_active_window() -> str:
    """Captures a screenshot of the currently active window and saves it. Returns the file path."""
    try:
        active = gw.getActiveWindow()
        if active is None:
            return capture_full_screen()

        bbox = {
            "left": active.left,
            "top": active.top,
            "width": active.width,
            "height": active.height,
        }
    except Exception:
        return capture_full_screen()

    with mss.mss() as sct:
        screenshot = sct.grab(bbox)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        filepath = os.path.join(SCREENSHOT_DIR, f"screen_{uuid.uuid4().hex[:8]}.png")
        img.save(filepath)
        return filepath

def capture_full_screen() -> str:
    """Fallback: captures the entire primary monitor."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        filepath = os.path.join(SCREENSHOT_DIR, f"screen_{uuid.uuid4().hex[:8]}.png")
        img.save(filepath)
        return filepath