import threading

class SharedState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SharedState, cls).__new__(cls)
                cls._instance.data = {
                    "last_modified_file": None,
                    "last_log_line": None,
                    "metric_accuracy": None,
                    "metric_loss": None,
                    "system_cpu": None,
                    "system_ram": None,
                    "system_gpu_util": None,
                    "clipboard_content": None,
                    "assistant_status": "idle"
                }
                cls._instance.data_lock = threading.Lock()
        return cls._instance

    def update(self, key, value):
        with self.data_lock:
            self.data[key] = value

    def get(self, key):
        with self.data_lock:
            return self.data.get(key)
            
    def get_all(self):
        with self.data_lock:
            return self.data.copy()

# Global singleton to import across the app
store = SharedState()
