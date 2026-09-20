import time
import os
import sys
import psutil
import subprocess

# Adjust import path so it can find the state_store
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

def get_gpu_stats():
    """
    Calls nvidia-smi to get GPU utilization and memory usage.
    Returns a dict with 'util_percent', 'mem_used_mb', and 'mem_total_mb' or None if it fails.
    """
    try:
        # --query-gpu asks for specific fields, --format=csv,noheader,nounits gives raw numbers
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            encoding="utf-8"
        )
        parts = result.strip().split(",")
        if len(parts) == 3:
            return {
                "util_percent": float(parts[0].strip()),
                "mem_used_mb": float(parts[1].strip()),
                "mem_total_mb": float(parts[2].strip())
            }
    except Exception as e:
        # Fails silently if nvidia-smi isn't found (e.g., no GPU)
        return None

def start_system_monitor(interval_seconds=2):
    print("[SystemMonitor] Starting hardware tracking...")
    
    while True:
        # 1. CPU & RAM
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_percent = psutil.virtual_memory().percent
        
        store.update("system_cpu", cpu_percent)
        store.update("system_ram", ram_percent)
        
        # 2. GPU
        gpu_stats = get_gpu_stats()
        if gpu_stats:
            # We'll store a formatted string for now, or you can split them into separate keys later
            gpu_str = f"{gpu_stats['util_percent']}% Util, {gpu_stats['mem_used_mb']}MB/{gpu_stats['mem_total_mb']}MB"
            store.update("system_gpu_util", gpu_str)
        
        if not store.get("is_confirming"):
            print(f"[SystemMonitor] CPU: {cpu_percent}%, RAM: {ram_percent}%, GPU: {store.get('system_gpu_util')}")
        
        time.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        # Initial call to cpu_percent with interval=0.1 to prime it, otherwise it returns 0.0 first time
        psutil.cpu_percent(interval=0.1)
        start_system_monitor()
    except KeyboardInterrupt:
        print("\nSystem monitor stopped.")
