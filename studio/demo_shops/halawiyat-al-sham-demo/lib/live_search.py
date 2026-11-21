"""
Live "Find for my business" search.

Sources (all live, nothing made up):
* postcodes.io            — UK postcode -> latitude/longitude (free, no key)
* OpenStreetMap Overpass  — nearby wholesalers, storage, couriers, banks, community shops (free, no key)
* Web search, pluggable   — Brave Search API (key), SerpAPI (key, Bing engine), DuckDuckGo HTML (no key)

Every result carries its URL, where it came from, the language of the search
phrase and the date/time it was checked. Nothing is ever marked verified:
results are "found live, not checked by us".

Results are cached per query for 24 hours in studio/data/cache/ to be kind to
the free services. Standard library only.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
import threading
import time
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from netutil import NetError, fetch
import communities

CACHE_TTL = 24 * 3600
LABEL = "found live, not checked by us"
OVERPASS_URLS = ["https://overpass-api.de/api/interpreter", "https://overpass-api.de/api/interpreter",
                 "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]   # main server twice (it is often briefly busy), then a mirror
POSTCODES_URL = "https://api.postcodes.io/postcodes/"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# --------------------------------------------------------------------- cache
class Cache:
    def __init__(self, path: Path, ttl: int = CACHE_TTL):
        self.path = Path(path)
        self.ttl = ttl
        self.lock = threading.RLock()

    def _load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except ValueError:
                return {}
        return {}

    @staticmethod
    def key(*parts: Any) -> str:
        return hashlib.sha256(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:32]

    def get(self, k: str) -> Optional[Any]:
        with self.lock:
            e = self._load().get(k)
            if e and time.time() - e["t"] < self.ttl:
                return e
            return None

    def put(self, k: str, data: Any) -> Dict[str, Any]:
        with self.lock:
            d = self._load()
            now = time.time()
            d = {kk: v for kk, v in d.items() if now - v["t"] < self.ttl}   # drop stale entries
            d[k] = {"t": now, "checked_at": now_iso(), "data": data}
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            return d[k]


# ------------------------------------------------------------------ postcode
POSTCODE_RE = re.compile(r"^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$", re.I)


def normalise_postcode(pc: str) -> str:
    pc = re.sub(r"\s+", "", (pc or "").upper())
    return pc[:-3] + " " + pc[-3:] if len(pc) > 3 else pc


def parse_postcode(payload: Dict[str, Any]) -> Dict[str, Any]:
    r = (payload or {}).get("result")
    if not r:
        raise NetError("bad_data", "postcodes.io did not return a location for that postcode.")
    return {"postcode": r["postcode"], "lat": r["latitude"], "lon": r["longitude"],
            "area": r.get("admin_district") or r.get("parish") or "",
            "ward": r.get("admin_ward") or "", "region": r.get("region") or "",
            "country": r.get("country") or "",
            "in_london": (r.get("region") == "London"),
            "source": "postcodes.io", "source_url": POSTCODES_URL + urllib.parse.quote(r["postcode"])}


def lookup_postcode(pc: str, fetcher: Callable = fetch, cache: Optional[Cache] = None, contact: str = "") -> Dict[str, Any]:
    npc = normalise_postcode(pc)
    if not POSTCODE_RE.match(npc):
        raise NetError("bad_data", f"'{pc}' doesn't look like a UK postcode (for example HA3 5AA).")
    k = Cache.key("postcode", npc)
    if cache:
        hit = cache.get(k)
        if hit:
            return dict(hit["data"], checked_at=hit["checked_at"], cached=True)
    try:
        _, _, raw = fetcher(POSTCODES_URL + urllib.parse.quote(npc), headers={"Accept": "application/json"},
                            timeout=15, contact=contact)
    except NetError as e:
        if e.status == 404:
            raise NetError("bad_data", f"postcodes.io doesn't know the postcode {npc}. Check it with the owner.")
        raise
    loc = parse_postcode(json.loads(raw.decode("utf-8")))
    e = cache.put(k, loc) if cache else {"checked_at": now_iso()}
    return dict(loc, checked_at=e["checked_at"], cached=False)


# ------------------------------------------------------------------ overpass
FOOD_SHOPS = ("supermarket|convenience|deli|butcher|greengrocer|bakery|pastry|confectionery|food|wholesale|general|"
              "frozen_food|seafood|spices|beverages|alcohol|variety_store")

# "cash and carry" in the name only counts for food/grocery shop types (not bathroom or bicycle "cash & carry").
MAP_FEATURES: Dict[str, List[str]] = {
    "suppliers": ['["shop"="wholesale"]', '["wholesale"]',
                  '["shop"~"^(' + FOOD_SHOPS + ')$"]["name"~"cash ?(and|&|n) ?carry|wholesale",i]'],
    "stock": ['["shop"="wholesale"]', '["shop"~"^(' + FOOD_SHOPS + ')$"]["name"~"cash ?(and|&|n) ?carry|wholesale",i]'],
    "finance": ['["amenity"="bank"]', '["amenity"="bureau_de_change"]', '["amenity"="money_transfer"]',
                '["office"="accountant"]', '["office"="financial"]'],
    "delivery": ['["amenity"="post_office"]', '["amenity"="parcel_locker"]', '["office"="courier"]',
                 '["amenity"="post_depot"]', '["office"="logistics"]'],
    "storage": ['["shop"="storage_rental"]', '["amenity"="storage_rental"]',
                '["shop"]["name"~"self ?storage|storage centre|storage units",i]'],   # (a name search over all warehouse buildings timed out on the free server, 26 Sept 2026)
    "other": [],
}


def _ovp_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_overpass_query(category: str, lat: float, lon: float, radius_m: int, community_regex: str = "") -> str:
    radius_m = max(200, min(int(radius_m), 15000))
    around = f"(around:{radius_m},{lat:.6f},{lon:.6f})"
    parts = [f"nwr{around}{f};" for f in MAP_FEATURES.get(category, [])]
    if community_regex and category in ("suppliers", "stock"):
        parts.append(f'nwr{around}["shop"~"^({FOOD_SHOPS})$"]["name"~"{_ovp_escape(community_regex)}",i];')
    elif community_regex and category == "other":
        parts.append(f'nwr{around}["shop"]["name"~"{_ovp_escape(community_regex)}",i];')
    if not parts:
        return ""
    return "[out:json][timeout:25];(" + "".join(parts) + ");out center tags 80;"


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


KIND_WORDS = [("shop", "wholesale", "Wholesaler"), ("shop", "storage_rental", "Self storage"),
              ("amenity", "storage_rental", "Storage"), ("amenity", "bank", "Bank"),
              ("amenity", "bureau_de_change", "Currency exchange"), ("amenity", "money_transfer", "Money transfer"),
              ("office", "accountant", "Accountant"), ("office", "financial", "Financial office"),
              ("amenity", "post_office", "Post office"), ("amenity", "parcel_locker", "Parcel locker"),
              ("office", "courier", "Courier"), ("amenity", "post_depot", "Delivery depot"),
              ("office", "logistics", "Logistics")]


def _kind(tags: Dict[str, str]) -> str:
    for k, v, label in KIND_WORDS:
        if tags.get(k) == v:
            return label
    if tags.get("wholesale"):
        return f"Wholesale ({tags['wholesale']})"
    if tags.get("shop"):
        return "Shop: " + tags["shop"].replace("_", " ")
    return "Place"


def parse_overpass(payload: Dict[str, Any], lat: float, lon: float, checked_at: str,
                   community_regex: str = "") -> List[Dict[str, Any]]:
    out, seen = [], set()
    rx = re.compile(community_regex, re.I) if community_regex else None
    for el in (payload or {}).get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("brand") or tags.get("operator")
        if not name:
            continue
        la = el.get("lat", (el.get("center") or {}).get("lat"))
        lo = el.get("lon", (el.get("center") or {}).get("lon"))
        if la is None or lo is None:
            continue
        key = (el.get("type"), el.get("id"))
        if key in seen:
            continue
        seen.add(key)
        addr = " ".join(x for x in [tags.get("addr:housenumber"), tags.get("addr:street")] if x)
        addr = ", ".join(x for x in [addr, tags.get("addr:city") or tags.get("addr:suburb"), tags.get("addr:postcode")] if x)
        d = haversine_m(lat, lon, la, lo)
        out.append({
            "title": name, "kind": _kind(tags), "address": addr or "No address in OpenStreetMap",
            "distance_m": round(d), "distance_text": f"{d / 1609.344:.1f} miles" if d >= 400 else f"{round(d)} m",
            "lat": la, "lon": lo,
            "url": f"https://www.openstreetmap.org/{el.get('type')}/{el.get('id')}",
            "website": tags.get("website") or tags.get("contact:website"),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "opening_hours": tags.get("opening_hours"),
            "community_match": bool(rx and rx.search(name)),
            "source": "map (OpenStreetMap)", "query_lang": "map", "checked_at": checked_at, "label": LABEL,
        })
    out.sort(key=lambda r: r["distance_m"])
    return out[:60]


def search_map(category: str, loc: Dict[str, Any], radius_m: int, community_regex: str = "",
               fetcher: Callable = fetch, cache: Optional[Cache] = None, contact: str = "") -> Dict[str, Any]:
    q = build_overpass_query(category, loc["lat"], loc["lon"], radius_m, community_regex)
    if not q:
        return {"results": [], "query": "", "note": "No map search for this category."}
    k = Cache.key("overpass", q)
    if cache:
        hit = cache.get(k)
        if hit:
            return {"results": parse_overpass(hit["data"], loc["lat"], loc["lon"], hit["checked_at"], community_regex),
                    "query": q, "cached": True, "checked_at": hit["checked_at"]}
    last: Optional[NetError] = None
    for url in OVERPASS_URLS:
        try:
            _, _, raw = fetcher(url, method="POST", data=urllib.parse.urlencode({"data": q}).encode(),
                                headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=40, contact=contact)
            payload = json.loads(raw.decode("utf-8"))
            e = cache.put(k, payload) if cache else {"checked_at": now_iso()}
            return {"results": parse_overpass(payload, loc["lat"], loc["lon"], e["checked_at"], community_regex),
                    "query": q, "cached": False, "checked_at": e["checked_at"], "endpoint": url}
        except NetError as ex:
            last = ex
            if ex.kind == "offline":
                break
            time.sleep(2)
        except ValueError:
            last = NetError("bad_data", "OpenStreetMap sent back something unexpected.")
    if last and last.kind in ("http", "timeout") and (last.status in (429, 502, 503, 504) or last.kind == "timeout"):
        raise NetError(last.kind, f"OpenStreetMap's free map servers are busy right now ({last.status or 'timed out'}), "
                                  "after trying 3 times. Please try again in a minute.", last.status)
    raise last or NetError("http", "OpenStreetMap map search failed.")


# ------------------------------------------------------------ web providers
class WebProvider:
    name = "base"
    label = "Web"
    needs_key = False

    def __init__(self, key: str = "", fetcher: Callable = fetch, contact: str = ""):
        self.key, self.fetch, self.contact = key, fetcher, contact

    def available(self) -> bool:
        return bool(self.key) or not self.needs_key

    def search(self, q: str, lang: str = "en") -> List[Dict[str, str]]:
        raise NotImplementedError


def _strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


class BraveProvider(WebProvider):
    """Brave Search API — https://api.search.brave.com/res/v1/web/search (header X-Subscription-Token)."""
    name, label, needs_key = "brave", "Brave Search", True

    def search(self, q, lang="en"):
        params = {"q": q, "count": 10, "country": "gb"}
        url = "https://api.search.brave.com/res/v1/web/search?" + urllib.parse.urlencode(params)
        _, _, raw = self.fetch(url, headers={"Accept": "application/json", "X-Subscription-Token": self.key},
                               timeout=20, contact=self.contact)
        return parse_brave(json.loads(raw.decode("utf-8")))


def parse_brave(d: Dict[str, Any]) -> List[Dict[str, str]]:
    return [{"title": _strip_tags(r.get("title")), "url": r.get("url"), "snippet": _strip_tags(r.get("description")),
             "age": r.get("age") or r.get("page_age")} for r in ((d or {}).get("web") or {}).get("results", []) if r.get("url")]


class SerpApiProvider(WebProvider):
    """SerpAPI with the Bing engine (we don't scrape Google) — https://serpapi.com/search.json"""
    name, label, needs_key = "serpapi", "SerpAPI (Bing)", True

    def search(self, q, lang="en"):
        url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(
            {"engine": "bing", "q": q, "cc": "GB", "api_key": self.key})
        _, _, raw = self.fetch(url, headers={"Accept": "application/json"}, timeout=25, contact=self.contact)
        return parse_serpapi(json.loads(raw.decode("utf-8")))


def parse_serpapi(d):
    if d and d.get("error"):
        raise NetError("http", "SerpAPI: " + str(d["error"]))
    return [{"title": r.get("title", ""), "url": r.get("link"), "snippet": r.get("snippet", "")}
            for r in (d or {}).get("organic_results", []) if r.get("link")]


class _DDGParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results: List[Dict[str, str]] = []
        self._in_title = self._in_snip = False
        self._cur: Dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if tag == "a" and "result__a" in cls:
            self._cur = {"title": "", "url": _ddg_url(a.get("href", "")), "snippet": ""}
            self.results.append(self._cur)
            self._in_title = True
        elif "result__snippet" in cls and self.results:
            self._in_snip = True

    def handle_endtag(self, tag):
        if tag == "a" and self._in_title:
            self._in_title = False
        elif tag in ("a", "div", "td") and self._in_snip:
            self._in_snip = False

    def handle_data(self, data):
        if self._in_title:
            self._cur["title"] += data
        elif self._in_snip and self.results:
            self.results[-1]["snippet"] += data


def _ddg_url(href: str) -> str:
    if "uddg=" in href:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return qs.get("uddg", [href])[0]
    return "https:" + href if href.startswith("//") else href


def parse_duckduckgo(page: str) -> List[Dict[str, str]]:
    if "anomaly" in page and "result__a" not in page:
        raise NetError("blocked", "DuckDuckGo asked this device to prove it's not a robot, so it gave no results. "
                                  "This often happens on cloud servers; it usually works from a home or phone connection. "
                                  "For reliable results add a Brave Search key in Settings.")
    p = _DDGParser()
    p.feed(page)
    out = []
    for r in p.results:
        u = r["url"]
        if not u.startswith("http") or "duckduckgo.com/y.js" in u:     # skip adverts
            continue
        out.append({"title": " ".join(r["title"].split()), "url": u, "snippet": " ".join(r["snippet"].split())})
    return out


class DuckDuckGoProvider(WebProvider):
    """DuckDuckGo HTML endpoint (no key). Polite: one request at a time, a pause between, clear failures."""
    name, label, needs_key = "duckduckgo", "DuckDuckGo", False
    _last = 0.0
    _lock = threading.Lock()

    def search(self, q, lang="en"):
        with DuckDuckGoProvider._lock:
            wait = 1.5 - (time.time() - DuckDuckGoProvider._last)
            if wait > 0:
                time.sleep(wait)
            DuckDuckGoProvider._last = time.time()
        _, _, raw = self.fetch("https://html.duckduckgo.com/html/", method="POST",
                               data=urllib.parse.urlencode({"q": q, "kl": "uk-en"}).encode(),
                               headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "text/html"},
                               timeout=20, contact=self.contact)
        return parse_duckduckgo(raw.decode("utf-8", "replace"))


PROVIDERS = {"brave": BraveProvider, "serpapi": SerpApiProvider, "duckduckgo": DuckDuckGoProvider}


def make_providers(settings: Dict[str, Any], fetcher: Callable = fetch) -> List[WebProvider]:
    keys = {"brave": settings.get("brave_api_key", ""), "serpapi": settings.get("serpapi_key", ""), "duckduckgo": ""}
    out = []
    for n in settings.get("provider_order") or ["brave", "serpapi", "duckduckgo"]:
        if n in PROVIDERS:
            p = PROVIDERS[n](keys.get(n, ""), fetcher, settings.get("contact_email", ""))
            if p.available():
                out.append(p)
    return out


def web_search_one(q: Dict[str, Any], providers: List[WebProvider], cache: Optional[Cache]) -> Dict[str, Any]:
    """Try providers in order until one works. Returns results + any provider errors."""
    errors = []
    for p in providers:
        k = Cache.key("web", p.name, q["q"])
        hit = cache.get(k) if cache else None
        if hit:
            rows, checked, cached = hit["data"], hit["checked_at"], True
        else:
            try:
                rows = p.search(q["q"], q["lang"])
            except NetError as e:
                errors.append({"provider": p.label, "kind": e.kind, "message": str(e)})
                if e.kind == "offline":
                    break
                continue
            except (ValueError, KeyError) as e:
                errors.append({"provider": p.label, "kind": "bad_data", "message": f"Unexpected answer ({e})."})
                continue
            e2 = cache.put(k, rows) if cache else {"checked_at": now_iso()}
            checked, cached = e2["checked_at"], False
        return {"results": [dict(r, source=f"web ({p.label})", provider=p.name, query=q["q"], query_lang=q["lang"],
                                 query_lang_name=q["lang_name"], dir=q.get("dir", "ltr"), checked_at=checked, label=LABEL)
                            for r in rows[:8]],
                "provider": p.label, "cached": cached, "errors": errors}
    return {"results": [], "provider": None, "cached": False, "errors": errors}


# -------------------------------------------------------------- orchestrate
def run_search(params: Dict[str, Any], settings: Dict[str, Any], cache: Optional[Cache] = None,
               fetcher: Callable = fetch) -> Dict[str, Any]:
    category = params.get("category") or "suppliers"
    community = params.get("community") or "other"
    free_text = (params.get("free_text") or "").strip()
    postcode = (params.get("postcode") or "").strip()
    radius = int(params.get("radius_m") or 3000)
    want_web = params.get("web", True)
    want_map = params.get("map", True)
    if category == "other" and not free_text:
        raise ValueError("For 'Anything else', type what the owner is looking for.")
    contact = settings.get("contact_email", "")
    out: Dict[str, Any] = {"category": category, "category_label": communities.CATEGORIES.get(category),
                           "community": community, "started_at": now_iso(), "label": LABEL,
                           "location": None, "queries": [], "web": [], "map": [], "errors": [], "notes": []}
    loc = None
    if postcode:
        try:
            loc = lookup_postcode(postcode, fetcher, cache, contact)
            out["location"] = loc
        except NetError as e:
            out["errors"].append({"provider": "postcodes.io", "kind": e.kind, "message": str(e)})
    area = (loc or {}).get("area") or params.get("area") or "London"
    in_london = (loc or {}).get("in_london", True)
    queries = communities.build_queries(community, category, area, in_london, free_text)
    max_q = int(settings.get("max_web_queries") or 6)
    # keep a mix: first English phrase(s) plus native-language phrases
    en = [q for q in queries if q["lang"] == "en"]
    native = [q for q in queries if q["lang"] != "en"]
    chosen = (en[:2] + native + en[2:])[:max_q]
    out["queries"] = [dict(q, used=(q in chosen)) for q in queries]
    if want_web:
        providers = make_providers(settings, fetcher)
        seen = set()
        offline = False
        for q in chosen:
            if offline:
                break
            r = web_search_one(q, providers, cache)
            for e in r["errors"]:
                e = dict(e, query=q["q"])
                if e["kind"] == "offline" and loc:
                    # we reached postcodes.io a moment ago, so the device is online: this one service dropped us
                    e.update(kind="connection", message=f"Couldn't connect to {e['provider']} (the connection was refused or "
                                                         "dropped). The device itself is online.")
                out["errors"].append(e)
                offline = offline or e["kind"] == "offline"
            for row in r["results"]:
                if row["url"] not in seen:
                    seen.add(row["url"])
                    out["web"].append(row)
        web_empty_offline = (not out["web"], offline)
    if want_map:
        if loc:
            c = communities.BY_ID.get(community, communities.BY_ID["other"])
            try:
                m = search_map(category, loc, radius, c.get("map_regex", ""), fetcher, cache, contact)
                out["map"] = m["results"]
                out["map_query"] = m.get("query")
                if not m["results"]:
                    out["notes"].append(f"OpenStreetMap has nothing tagged for this within {radius / 1000:.1f} km. "
                                        "Try a bigger radius. (Not every shop is on OpenStreetMap.)")
            except NetError as e:
                out["errors"].append({"provider": "OpenStreetMap (Overpass)", "kind": e.kind, "message": str(e)})
        else:
            out["notes"].append("Add the shop's postcode to see nearby places on the map.")
    out["finished_at"] = now_iso()
    if want_web and web_empty_offline[0]:
        out["notes"].append("No web results came back. " + (
            "The device looks offline." if web_empty_offline[1] else
            "The web search services refused or returned nothing (see the messages)."
            + (" The map results below still came through." if out["map"] else "")))
    return out
