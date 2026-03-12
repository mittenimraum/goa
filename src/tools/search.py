class SearchToolError(Exception):
    pass

def web_search(query: str, max_results: int = 3) -> str:
    return ""