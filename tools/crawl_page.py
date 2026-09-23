import requests
from bs4 import BeautifulSoup

def crawl_page(url: str) -> str:
    """Fetches a URL and extracts clean readable text. Cheap, fast path for simple static
    pages (docs, articles, READMEs). Use this by default; only use extract_from_page if you
    need a specific targeted answer rather than the full page content."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # strip script/style tags, they add noise
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # crude signal for "this page needs JS rendering" — very little real content
        if len(text) < 200:
            return f"[Page returned very little content — may require JS rendering. Consider extract_from_page instead.]\n\n{text}"

        return text[:5000]  # cap length so it doesn't blow out context
    except Exception as e:
        return f"Failed to fetch page: {e}"
