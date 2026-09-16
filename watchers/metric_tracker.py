import re
import os
import sys

# Adjust import path so it can find the state_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

# Regex patterns to catch things like "loss=0.692, accuracy=0.60"
# or "Loss: 0.5", etc.
LOSS_PATTERN = re.compile(r"loss[\s:=]+([0-9]*\.?[0-9]+)", re.IGNORECASE)
ACC_PATTERN = re.compile(r"acc(?:uracy)?[\s:=]+([0-9]*\.?[0-9]+)", re.IGNORECASE)

def process_log_line(line):
    """
    Parses a single log line. If it contains metrics, updates the state.
    """
    loss_match = LOSS_PATTERN.search(line)
    acc_match = ACC_PATTERN.search(line)
    
    updated = False
    
    if loss_match:
        loss_val = float(loss_match.group(1))
        store.update("metric_loss", loss_val)
        updated = True
        
    if acc_match:
        acc_val = float(acc_match.group(1))
        store.update("metric_accuracy", acc_val)
        updated = True
        
    if updated:
        print(f"[MetricTracker] Parsed -> Loss: {store.get('metric_loss')}, Accuracy: {store.get('metric_accuracy')}")
