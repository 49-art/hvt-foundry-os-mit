"""Web search connectors: Brave Search API (key) and DuckDuckGo HTML (no key)."""
import sys
from pathlib import Path
from . import Connector, ConnectorError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import live_search  # noqa: E402


class BraveSearch(Connector):
    id = "brave_search"
    name = "Brave Search API"
    category = "Search"
    cost_type = "paid"
    what_it_does = "Reliable web search for the 'Find for my business' screen."
    credentials = [{"key": "api_key", "label": "Brave Search API key", "secret": True, "required": True,
                    "help": "api-dashboard.search.brave.com → API keys. Also used if saved in Settings."}]
    docs_url = "https://api-dashboard.search.brave.com/app/documentation/web-search/get-started"
    pricing = {"text": "Search: $5 per 1,000 requests, prepaid. A card is needed even for the free credit.",
               "url": "https://api-dashboard.search.brave.com/app/plans", "checked": "2026-09-26"}
    status = "code-ready-needs-key"
    status_note = "Endpoint and header confirmed on brave.com/search/api on 2026-09-26. Without a key the API answered 422 'x-subscription-token required', so the address is right."
    actions = {"search": {"label": "Search the web", "params": [{"key": "q", "label": "Search for", "example": "Polish wholesaler London"}]}}

    def test_connection(self):
        self.need("api_key")
        rows = live_search.BraveProvider(self.creds["api_key"], self.fetch, self.contact).search("cash and carry Harrow")
        return {"ok": True, "message": f"Working: {len(rows)} results for 'cash and carry Harrow'."}

    def act_search(self, p):
        self.need("api_key")
        if not p.get("q"):
            raise ConnectorError("Type something to search for.")
        return {"results": live_search.BraveProvider(self.creds["api_key"], self.fetch, self.contact).search(p["q"])}


class DuckDuckGo(Connector):
    id = "duckduckgo"
    name = "DuckDuckGo (no key)"
    category = "Search"
    cost_type = "free"
    what_it_does = "Free web search fallback. Can refuse cloud servers with a robot check; usually fine from a home or phone connection."
    docs_url = "https://html.duckduckgo.com/html/"
    pricing = {"text": "Free, no key. Not an official API: it can stop working at any time.", "url": "https://duckduckgo.com/", "checked": "2026-09-26"}
    status = "unverified"
    status_note = ("Tested from our cloud box on 2026-09-26: DuckDuckGo answered with a robot check (HTTP 202, 'anomaly'), "
                   "so no results. The Studio says so clearly when this happens. Not yet tested from a home connection.")
    actions = {"search": {"label": "Search the web", "params": [{"key": "q", "label": "Search for", "example": "Romanian shop Harrow"}]}}

    def test_connection(self):
        rows = live_search.DuckDuckGoProvider("", self.fetch, self.contact).search("cash and carry Harrow")
        return {"ok": True, "message": f"Working from this device: {len(rows)} results."}

    def act_search(self, p):
        if not p.get("q"):
            raise ConnectorError("Type something to search for.")
        return {"results": live_search.DuckDuckGoProvider("", self.fetch, self.contact).search(p["q"])}
