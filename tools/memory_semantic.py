import chromadb
import ollama
import uuid
import os

CHROMA_PATH = "state_store/chroma"
os.makedirs(CHROMA_PATH, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_PATH)
memory_collection = client.get_or_create_collection("semantic_memory")

def embed(text: str):
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]

def save_memory(fact: str) -> str:
    """Saves a durable fact about the user or their projects for recall in future sessions.
    Use this when the user shares a preference, a decision, or a fact worth remembering
    long-term (e.g. 'I'm using PyTorch for this project', 'I prefer concise answers')."""
    try:
        memory_collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[embed(fact)],
            documents=[fact],
        )
        return "Saved."
    except Exception as e:
        return f"Failed to save memory: {e}"

def recall_memory(query: str, n_results: int = 3) -> str:
    """Retrieves previously saved facts relevant to a query."""
    try:
        results = memory_collection.query(query_embeddings=[embed(query)], n_results=n_results)
        if not results["documents"] or not results["documents"][0]:
            return "No relevant memory found."
        return "\n".join(results["documents"][0])
    except Exception as e:
        return f"Failed to recall memory: {e}"
