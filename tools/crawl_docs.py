from scrapegraphai.graphs import SmartScraperMultiGraph
from agent.confirmation import confirm_action

graph_config = {
    "llm": {
        "model": "ollama/qwen3.5-verora",
        "model_tokens": 8192,
        "base_url": "http://localhost:11434",
    },
    "headless": True,
}

MAX_PAGES_WITHOUT_CONFIRMATION = 5

def crawl_docs(urls: list[str], question: str) -> str:
    """Extracts an answer that may span multiple pages of a documentation site. Requires
    confirmation if the number of pages exceeds a small threshold, since wide crawls take
    longer and make more requests to the target site."""
    if len(urls) > MAX_PAGES_WITHOUT_CONFIRMATION:
        if not confirm_action(f"This will crawl {len(urls)} pages from these URLs:\n" + "\n".join(urls)):
            return "Crawl cancelled by user."

    try:
        scraper = SmartScraperMultiGraph(
            prompt=question,
            source=urls,
            config=graph_config,
        )
        result = scraper.run()
        return str(result)
    except Exception as e:
        return f"Multi-page crawl failed: {e}"
