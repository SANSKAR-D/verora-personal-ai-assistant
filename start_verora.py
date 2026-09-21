import sys
import os

# Force stdout/stderr to utf-8 to prevent UnicodeEncodeError on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Adjust import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from main_watchers import run_all_watchers
from agent.overlay import VeroraOverlay, signals
from agent.wake_word import start_wake_word_listener


if __name__ == "__main__":
    print("Initializing Verora Watchers...")
    
    # 1. Start all the background watchers on separate threads
    run_all_watchers()
    
    # 2. Setup the PyQt Application (MUST be on the main thread)
    app = QApplication(sys.argv)
    overlay = VeroraOverlay()
    
    # 3. Connect the Wake Word signals to the overlay UI
    signals.show_signal.connect(overlay.show_overlay)
    signals.hide_signal.connect(overlay.hide_overlay)
    
    # Map the text updates to our smart handler
    signals.update_signal.connect(overlay.handle_voice_update)
    
    # 4. Start the wake word listener in the background
    print("\n--- All Systems Go! ---")
    print("Holographic UI is hidden in the background.")
    print("Say 'Hey Verora' to wake Verora up!\n")
    start_wake_word_listener()
    
    # 5. Start the PyQt main event loop (this blocks forever until the app closes)
    sys.exit(app.exec())
