"""
Knowledge Builder Agent
-----------------------
Fetches factual text from trusted sources
(Wikipedia + DuckDuckGo) to build a dynamic KB.
"""

import requests
from bs4 import BeautifulSoup


# ---------------- Wikipedia Fetch ----------------

def fetch_wikipedia(query: str, max_chars=2000):
    """
    Fetch summary text from Wikipedia API.
    """
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")

    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None

        data = res.json()
        text = data.get("extract")
        return text[:max_chars] if text else None

    except Exception:
        return None


# ---------------- DuckDuckGo Fetch ----------------

def fetch_duckduckgo(query: str, max_chars=2000):
    """
    Fetch instant answer text from DuckDuckGo.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        text = data.get("AbstractText")
        return text[:max_chars] if text else None

    except Exception:
        return None


# ---------------- Agent Orchestrator ----------------

def build_dynamic_kb(query: str):
    """
    Main agent entry point.
    Returns a list of factual text chunks.
    """

    documents = []

    wiki_text = fetch_wikipedia(query)
    if wiki_text:
        documents.append(wiki_text)

    ddg_text = fetch_duckduckgo(query)
    if ddg_text:
        documents.append(ddg_text)

    return documents
