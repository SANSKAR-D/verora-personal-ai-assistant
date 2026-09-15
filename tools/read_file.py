def read_file(path: str) -> str:
    """Reads a project file directly from disk and returns its contents."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found at {path}"
    except Exception as e:
        return f"Error reading file: {e}"