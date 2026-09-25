import sqlite3
import json
import os

DB_PATH = "state_store/entities.db"

def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            name TEXT PRIMARY KEY,
            type TEXT,
            fields TEXT,
            last_updated TEXT
        )
    """)
    return conn

def upsert_entity(name: str, entity_type: str, fields: dict) -> str:
    """Creates or updates a structured record for a named entity — a project, a hosted
    model, a site config — with named fields rather than freeform text. Use this to track
    structured facts like 'AlphaGo-Lite: last_accuracy=0.74, architecture=CNN'."""
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO entities (name, type, fields, last_updated) VALUES (?, ?, ?, datetime('now')) "
            "ON CONFLICT(name) DO UPDATE SET fields=excluded.fields, last_updated=excluded.last_updated",
            (name, entity_type, json.dumps(fields)),
        )
        conn.commit()
        conn.close()
        return f"Entity '{name}' updated."
    except Exception as e:
        return f"Failed to upsert entity: {e}"

def query_entity(name: str) -> str:
    """Retrieves structured fields for a specific named entity by exact name."""
    try:
        conn = _get_conn()
        row = conn.execute("SELECT type, fields, last_updated FROM entities WHERE name = ?", (name,)).fetchone()
        conn.close()
        if not row:
            return f"No entity found named '{name}'."
        entity_type, fields, updated = row
        return f"{name} ({entity_type}), last updated {updated}:\n{fields}"
    except Exception as e:
        return f"Failed to query entity: {e}"
