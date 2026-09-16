import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Adjust import path so it can find the state_store
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

class ProjectEventHandler(FileSystemEventHandler):
    def __init__(self, ignore_dirs=None):
        self.ignore_dirs = ignore_dirs or ['.git', '.venv', '__pycache__', 'temp_audio']

    def is_ignored(self, event):
        # Ignore directory changes and specific folders
        if event.is_directory:
            return True
        for ignored in self.ignore_dirs:
            if f"\\{ignored}\\" in event.src_path or f"/{ignored}/" in event.src_path:
                return True
        return False

    def on_modified(self, event):
        if not self.is_ignored(event):
            filename = os.path.basename(event.src_path)
            # Update the central state
            store.update("last_modified_file", filename)
            print(f"[FileWatcher] Detected modification: {filename}")

def start_file_watcher(path_to_watch="."):
    event_handler = ProjectEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    print(f"FileWatcher started on {os.path.abspath(path_to_watch)}")
    return observer

if __name__ == "__main__":
    # Test the watcher independently
    obs = start_file_watcher()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
