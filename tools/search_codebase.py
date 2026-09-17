import chromadb
import ollama

CHROMA_PATH = "state_store/chroma"
COLLECTION_NAME = "codebase"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

def embed(text: str):
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]

def search_codebase(query: str, n_results: int = 5) -> str:
    """Semantic search over the indexed project codebase. Returns the most relevant code chunks for a query."""
    query_embedding = embed(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

    if not results["documents"] or not results["documents"][0]:
        return "No relevant code found."

    def rerank(query: str, chunks: list[str]) -> list[str]:
        """Ask the LLM to rank chunks by relevance, returning them reordered."""
        numbered = "\n\n".join(f"[{i}] {c[:200]}..." for i, c in enumerate(chunks))
        prompt = f"""Given this query: "{query}"
        Rank these code chunks by relevance (most relevant first). Reply with only the numbers, comma-separated, e.g. "2,0,1":{numbered}"""

        response = ollama.chat(model="qwen3.5-verora", messages=[{"role": "user", "content": prompt}])
        try:
            order = [int(x.strip()) for x in response["message"]["content"].split(",")]
            return [chunks[i] for i in order if i < len(chunks)]
        except Exception:
            return chunks  # fall back to original order if parsing fails

    output = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        output.append(f"--- {meta['file']} ---\n{doc}")

    return "\n\n".join(output)