import time
import os
import sys
import pyperclip

# Adjust import path so it can find the state_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

def start_clipboard_watcher(interval_seconds=1.0):
    print("[ClipboardWatcher] Started watching clipboard...")
    
    # Track the last known content to avoid spamming updates
    last_content = ""
    
    while True:
        try:
            # Get the current text from the clipboard
            current_content = pyperclip.paste()
            
            # If it's new and not empty, update the state
            if current_content and current_content != last_content:
                last_content = current_content
                
                # Truncate to avoid saving massive amounts of text into state if you copy a whole file
                truncated = current_content if len(current_content) < 1000 else current_content[:997] + "..."
                store.update("clipboard_content", truncated)
                
                # Just printing the first 50 chars so we don't spam the console
                preview = truncated.replace('\n', ' ')[:50]
                print(f"[ClipboardWatcher] New copied text: '{preview}...'")
                
        except pyperclip.PyperclipException:
            # Fails silently if clipboard is locked or inaccessible
            pass
            
        time.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        start_clipboard_watcher()
    except KeyboardInterrupt:
        print("\nClipboard watcher stopped.")
