import os
import hashlib
import uuid
import chromadb
import ollama

CHROMA_PATH = "state_store/chroma"
COLLECTION_NAME = "codebase"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".md", ".json", ".yaml", ".yml"}
IGNORE_DIRS = {".venv", ".git", "__pycache__", "node_modules", "temp_audio", "state_store", ".kilo"}

def file_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def embed(text: str):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]

def index_single_file(filepath: str, collection_ref=None):
    """Embeds a single file and replaces its old chunks in ChromaDB."""
    if collection_ref is None:
        collection_ref = collection

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return

    if not content.strip():
        return

    current_hash = file_hash(content)
    
    # Check if we already have this exact version
    existing = collection_ref.get(where={"file": filepath}, include=["metadatas"])
    if existing and existing["metadatas"]:
        # All chunks for this file should have the same hash, so just check the first one
        if existing["metadatas"][0].get("hash") == current_hash:
            return # Unchanged, skip embedding!

    # Hash is different! Delete old chunks for this file
    collection_ref.delete(where={"file": filepath})

    # Embed and add new chunks
    for chunk in chunk_text(content):
        embedding = embed(chunk)
        collection_ref.add(
            ids=[f"doc_{uuid.uuid4().hex[:8]}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"file": filepath, "hash": current_hash}],
        )
    print(f"[RAG] Re-indexed modified file: {os.path.basename(filepath)}")

def index_project(project_dir: str):
    print("Running smart indexer... (unchanged files will be skipped)")
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in files:
            ext = os.path.splitext(filename)[1]
            if ext not in CODE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            # Use our smart single file indexer for every file
            index_single_file(filepath, collection)
            
    print("Indexing complete.")

if __name__ == "__main__":
    index_project("C:/Users/seths/verora")
