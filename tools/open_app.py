import subprocess

APP_ALIASES = {
    "calculator": "calc",
    "powerpoint": "powerpnt",
    "word": "winword",
    "excel": "excel",
    "settings": "ms-settings:",
    "whatsapp": "whatsapp:",
    "spotify": "spotify:",
    "browser": "chrome",
}

def open_app(app_name: str) -> str:
    """
    Launches a NATIVE desktop application ONLY (e.g. 'notepad', 'calc').
    DO NOT use this for websites like Wikipedia or Google. Use 'automate_browser' instead.
    """
    try:
        # Check if the user used a common name instead of the exact Windows file name
        app_name_lower = app_name.lower().strip()
        if app_name_lower in APP_ALIASES:
            app_name = APP_ALIASES[app_name_lower]

        # On Windows, using 'start' allows it to find apps like chrome/edge without full paths
        if not app_name.lower().startswith("start "):
            app_name = f"start {app_name}"
            
        subprocess.Popen(app_name, shell=True)
        return f"Opened {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {e}"
