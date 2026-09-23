import os
from tavily import TavilyClient

# Initialize the client with the API key from .env
client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def web_search(query: str, max_results: int = 5) -> str:
    """Searches the web for current, relevant information. Returns clean, structured
    results well-suited for grounding an answer — use this for anything requiring
    up-to-date information the model might not know from training."""
    try:
        response = client.search(
            query=query, 
            max_results=max_results,
            # Use 'news' topic if you want the most recent info
            # topic="news", 
            # days=3 
        )
        results = response.get("results", [])

        if not results:
            return "No results found."

        output = []
        for r in results:
            output.append(f"{r['title']}\n{r['url']}\n{r['content']}\n")

        return "\n".join(output)
    except Exception as e:
        return f"Search failed: {e}"
