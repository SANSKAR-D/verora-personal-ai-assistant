import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.overlay import signals
from state_store.state import store

def close_overlay() -> str:
    """Hides the Verora overlay from the screen. Call this when the user asks to close, hide, or dismiss the overlay."""
    signals.hide_signal.emit()
    
    # Flip the switch in memory so the listening loop knows to stop!
    store.update("overlay_open", False)
    
    return "Overlay successfully closed and hidden from the screen."
