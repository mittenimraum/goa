import requests
from bs4 import BeautifulSoup

from models import SearchResult


class SearchToolError(Exception):
    pass

def web_search(query: str, max_results: int = 3) -> list[SearchResult]:
    try:
        url = "https://duckduckgo.com/html/"
        response = requests.get(url, params={"q": query}, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        html = response.text

        if "anomaly-modal" in html or "challenge-form" in html:
            raise SearchToolError("DuckDuckGo returned an anto bot challenge page")

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for node in soup.select(".result")[:max_results]:
            title_node = node.select_one(".result__title")
            link_node = node.select_one(".result__url")
            snippet_node = node.select_one(".result__snippet")

            title = title_node.get_text(" ", strip=True) if title_node else ""
            url_text = link_node.get_text(" ", strip=True) if link_node else ""
            snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""

            if title or snippet:
                result = SearchResult(title=title, url=url_text, snippet=snippet)
                results.append(result)

        if not results:
            return []

        return results

    except requests.RequestException as exc:
        raise SearchToolError(f"Web search request failed: {exc}") from exc
    except Exception as exc:
        raise SearchToolError(f"Web search parsing failed: {exc}") from exc
