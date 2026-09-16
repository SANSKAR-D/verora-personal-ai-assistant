import sys
import os

# Adjust import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_watchers import run_all_watchers
from agent.overlay import run_overlay

if __name__ == "__main__":
    print("Initializing Verora Watchers...")
    
    # 1. Start all the background watchers on separate threads
    run_all_watchers()
    
    # 2. Start the PyQt UI on the main thread (PyQt *requires* the main thread)
    print("Starting Holographic UI...")
    run_overlay()
