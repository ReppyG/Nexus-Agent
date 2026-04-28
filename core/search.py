import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

NEXUS_ROOT = os.path.expanduser("~/nexus")
ERROR_LOG_PATH = os.path.join(NEXUS_ROOT, "memory", "error_logs.json")
MAX_TEXT_PER_SOURCE = 1500


def _log_error(source, message):
    try:
        os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
        logs = []
        if os.path.exists(ERROR_LOG_PATH):
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source": source,
            "error": message
        })
        with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


def _scrape_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Nexus/1.0)"}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = " ".join(text.split())
        return text[:MAX_TEXT_PER_SOURCE]
    except Exception as e:
        _log_error("search._scrape_url", f"{url}: {e}")
        return ""


def web_research(query, max_results=2):
    results_text = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        _log_error("search.web_research", str(e))
        return f"Web search failed: {e}"

    for i, result in enumerate(results):
        title = result.get("title", "No title")
        url = result.get("href", "")
        snippet = result.get("body", "")

        scraped = ""
        if url:
            scraped = _scrape_url(url)

        content = scraped if scraped else snippet
        results_text.append(
            f"Source {i + 1}: {title}\nURL: {url}\nContent: {content}"
        )

    if not results_text:
        return "No web results found."

    return "\n\n---\n\n".join(results_text)


if __name__ == "__main__":
    print("Testing search module...")
    query = "Python asyncio tutorial"
    print(f"Searching for: {query}")
    result = web_research(query, max_results=2)
    print("Result preview:")
    print(result[:500])
    print("\nSearch module OK.")
