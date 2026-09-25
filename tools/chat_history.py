import json
import os
from langchain_core.messages import messages_to_dict, messages_from_dict

HISTORY_PATH = "state_store/chat_history.json"

def load_chat_history() -> list:
    """Loads persistent chat history from disk."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return messages_from_dict(data)
    except Exception as e:
        print(f"[Memory] Failed to load chat history: {e}")
        return []

def save_chat_history(messages: list):
    """Saves chat history to disk."""
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    try:
        # Strip system messages before saving so we don't save the massive dynamic prompt
        clean_messages = [m for m in messages if getattr(m, "type", "") != "system"]
        data = messages_to_dict(clean_messages)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Memory] Failed to save chat history: {e}")
