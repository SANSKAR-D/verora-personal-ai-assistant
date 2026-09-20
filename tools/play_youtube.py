import pywhatkit

def play_youtube(song_name: str) -> str:
    """
    Searches YouTube for a song or video and automatically clicks play on the first result in the user's visible browser!
    """
    try:
        # This magically opens the browser, searches, and clicks the first video automatically!
        pywhatkit.playonyt(song_name)
        return f"Successfully opened the visible browser and started playing '{song_name}' on YouTube!"
    except Exception as e:
        return f"Failed to play video: {e}"
