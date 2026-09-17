import time
import os
import sys
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Adjust import path so it can find the state_store and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

# --- NEW: Import the smart indexer ---
from tools.index_codebase import index_single_file, CODE_EXTENSIONS

class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, ignore_dirs=None):
        self.ignore_dirs = ignore_dirs or ['.git', '.venv', '__pycache__', 'temp_audio', 'state_store']

    def is_ignored(self, event):
        if event.is_directory:
            return True
        for ignored in self.ignore_dirs:
            if f"\\{ignored}\\" in event.src_path or f"/{ignored}/" in event.src_path:
                return True
        return False

    def on_modified(self, event):
        if not self.is_ignored(event):
            filename = os.path.basename(event.src_path)
            # Update the central state for the UI
            store.update("last_modified_file", filename)
            print(f"[FileWatcher] Detected modification: {filename}")
            
            # --- NEW: Trigger RAG re-indexing in the background ---
            ext = os.path.splitext(filename)[1]
            if ext in CODE_EXTENSIONS:
                # Run in a thread so Ollama embedding doesn't freeze the watcher
                threading.Thread(target=index_single_file, args=(event.src_path,)).start()

def start_file_watcher(path_to_watch="."):
    event_handler = ProjectEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    print(f"FileWatcher started on {os.path.abspath(path_to_watch)}")
    return observer

if __name__ == "__main__":
    obs = start_file_watcher()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
