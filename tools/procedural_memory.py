import sqlite3
import json
import os

DB_PATH = "state_store/procedural_memory.db"

def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            outcome TEXT,
            details TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        )
    """)
    return conn

def log_task_attempt(task: str, outcome: str, details: dict = None) -> str:
    """Records the outcome of a browser/automation task attempt, including failure
    reasons, so the same mistake isn't repeated blindly on the next attempt."""
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO task_attempts (task, outcome, details) VALUES (?, ?, ?)",
            (task, outcome, json.dumps(details or {})),
        )
        conn.commit()
        conn.close()
        return "Task attempt logged."
    except Exception as e:
        print(f"[ProceduralMemory] Failed to log task: {e}")
        return f"Failed to log task: {e}"

def recall_task_history(task: str, limit: int = 3) -> str:
    """Retrieves past attempts at a specific task before re-attempting it."""
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT outcome, details, timestamp FROM task_attempts WHERE task = ? ORDER BY timestamp DESC LIMIT ?",
            (task, limit),
        ).fetchall()
        conn.close()
        if not rows:
            return f"No prior attempts found for task '{task}'."
        return "\n".join(f"[{r[2]}] {r[0]} — {r[1]}" for r in rows)
    except Exception as e:
        print(f"[ProceduralMemory] Failed to recall task: {e}")
        return f"Failed to recall task: {e}"
