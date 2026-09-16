import time
import os
import sys

# Adjust import path so it can find the state_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

# --- NEW: Import the metric tracker ---
from watchers.metric_tracker import process_log_line

def start_log_tailer(log_file_path):
    print(f"Waiting for log file: {log_file_path}")
    
    while not os.path.exists(log_file_path):
        time.sleep(1)
        
    print(f"[LogTailer] Started tailing: {log_file_path}")
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
                
            line = line.strip()
            if line:
                store.update("last_log_line", line)
                print(f"[LogTailer] New line: {line}")
                
                # --- NEW: Process the line for metrics ---
                process_log_line(line)

if __name__ == "__main__":
    # If a filename is passed in the terminal, use it. Otherwise default to train.log
    if len(sys.argv) > 1:
        target_filename = sys.argv[1]
    else:
        target_filename = "train.log"
        
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), target_filename)
    
    try:
        start_log_tailer(log_path)
    except KeyboardInterrupt:
        print("\nLog tailer stopped.")

