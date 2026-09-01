from langchain_core.tools import tool
from ddgs import DDGS


@tool

def web_search(query: str) -> str:
    """Search the public web for current information and return several results."""
    results = DDGS().text(query, region="wt-wt", safesearch="moderate", max_results=5)
    items = list(results)

    if not items:
        return f'No web results found for "{query}".'

    lines = []
    for index, item in enumerate(items, start=1):
        title = item.get("title", "Untitled")
        url = item.get("href", "")
        snippet = item.get("body", "")
        lines.append(f"{index}. {title}\nURL: {url}\n{snippet}")

    return "\n\n".join(lines)
