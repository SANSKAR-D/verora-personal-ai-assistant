import sqlite3
import os

DB_PATH = "state_store/tasks.db"

def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    return conn

def add_task(description: str) -> str:
    """Adds a task to the local task tracker."""
    try:
        conn = _get_conn()
        conn.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        conn.commit()
        conn.close()
        return f"Added task: {description}"
    except Exception as e:
        return f"Failed to add task: {e}"

def list_tasks() -> str:
    """Lists all open (not completed) tasks."""
    try:
        conn = _get_conn()
        rows = conn.execute("SELECT id, description FROM tasks WHERE done = 0").fetchall()
        conn.close()
        if not rows:
            return "No open tasks."
        return "\n".join(f"[{r[0]}] {r[1]}" for r in rows)
    except Exception as e:
        return f"Failed to list tasks: {e}"

def complete_task(task_id: int) -> str:
    """Marks a task as completed by its ID."""
    try:
        conn = _get_conn()
        conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return f"Marked task {task_id} as complete."
    except Exception as e:
        return f"Failed to complete task: {e}"
