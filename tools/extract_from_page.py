from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/qwen3.5-verora",
        "model_tokens": 8192,
        "base_url": "http://localhost:11434",
    },
    "headless": True,
}

def extract_from_page(url: str, question: str) -> str:
    """Extracts a specific, targeted answer from a URL using the local LLM — use this when
    you need a specific piece of information from a page (e.g. a function signature, a
    changelog entry) rather than the whole page's content. For reading a full page as-is,
    use crawl_page instead."""
    try:
        scraper = SmartScraperGraph(
            prompt=question,
            source=url,
            config=graph_config,
        )
        result = scraper.run()
        return str(result)
    except Exception as e:
        return f"Extraction failed: {e}"
