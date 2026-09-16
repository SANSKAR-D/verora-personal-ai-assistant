import threading
import sys
import os
import time

# Adjust import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from watchers.file_watcher import start_file_watcher
from watchers.log_tailer import start_log_tailer
from watchers.system_monitor import start_system_monitor
from watchers.clipboard_watcher import start_clipboard_watcher

def run_all_watchers():
    print("Starting all continuous watchers...")
    
    # 1. File watcher (already non-blocking)
    start_file_watcher(".")
    
    # 2. Log tailer (run in background thread)
    log_path = os.path.join(os.path.dirname(__file__), "train.log")
    threading.Thread(target=start_log_tailer, args=(log_path,), daemon=True).start()
    
    # 3. System monitor (run in background thread)
    threading.Thread(target=start_system_monitor, args=(2,), daemon=True).start()
    
    # 4. Clipboard watcher (run in background thread)
    threading.Thread(target=start_clipboard_watcher, args=(1.0,), daemon=True).start()
    
    print("\n--- All Watchers Active! ---\n")

if __name__ == "__main__":
    run_all_watchers()
    
    # Keep the main thread alive so the background threads keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all watchers.")
