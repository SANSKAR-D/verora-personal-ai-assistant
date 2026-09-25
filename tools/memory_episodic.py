import chromadb
import ollama
import uuid
import os
from datetime import datetime

CHROMA_PATH = "state_store/chroma"
os.makedirs(CHROMA_PATH, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_PATH)
episode_collection = client.get_or_create_collection("episodic_memory")

def embed(text: str):
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]

def log_episode(task: str, question: str, outcome: str) -> str:
    """Records a completed interaction as a discrete, timestamped event — what was asked,
    what was done, what happened. Call this after any meaningful interaction is resolved."""
    try:
        entry = f"[{datetime.now().isoformat()}] Task: {task}\nQuestion: {question}\nOutcome: {outcome}"
        episode_collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embed(entry)],
            documents=[entry],
            metadatas=[{"task": task, "timestamp": datetime.now().isoformat()}],
        )
        return "Episode logged."
    except Exception as e:
        return f"Failed to log episode: {e}"

def recall_episodes(query: str, n_results: int = 3) -> str:
    """Retrieves past interactions matching a topic — use this to check what was already
    tried or discussed before, e.g. 'what did we try last time for this bug'."""
    try:
        results = episode_collection.query(query_embeddings=[embed(query)], n_results=n_results)
        if not results["documents"] or not results["documents"][0]:
            return "No relevant past episodes found."
        return "\n\n".join(results["documents"][0])
    except Exception as e:
        return f"Failed to recall episodes: {e}"
