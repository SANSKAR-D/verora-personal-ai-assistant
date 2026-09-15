def tail_log(path: str, n: int = 50) -> str:
    """Reads the last N lines from a log file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-n:])
    except FileNotFoundError:
        return f"Error: log file not found at {path}"
    except Exception as e:
        return f"Error reading log: {e}"