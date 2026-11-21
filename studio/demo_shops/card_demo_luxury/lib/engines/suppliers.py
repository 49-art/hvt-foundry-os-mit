"""
Trade-aware supplier finder, built on the Studio's live search (lib/live_search.py).

A card says which OpenStreetMap tags and which web phrases fit its trade
(for hair: shop=hairdresser_supply and "hair and beauty wholesaler near …").
Everything returned is labelled "found live, not checked by us" with its link
and the time it was checked. Nothing is made up; empty results are reported as empty.
"""
from __future__ import annotations

import json
import urllib.parse
from typing import Any, Callable, Dict, List, Optional


def run(card_search: Dict[str, Any], postcode: str, settings: Dict[str, Any], fetcher: Callable,
        cache=None, radius_m: int = 5000, extra_text: str = "") -> Dict[str, Any]:
    import live_search as ls                              # from lib/ (shop app) or studio/ (Studio)
    out: Dict[str, Any] = {"label": ls.LABEL, "started_at": ls.now_iso(), "web": [], "map": [], "errors": [],
                           "notes": [], "queries": []}
    loc = None
    if postcode:
        try:
            loc = ls.lookup_postcode(postcode, fetcher, cache)
            out["location"] = loc
        except ls.NetError as e:
            out["errors"].append({"provider": "postcodes.io", "kind": e.kind, "message": str(e)})
    area = (loc or {}).get("area") or "London"
    phrases = [p.replace("{area}", area) for p in card_search.get("web_phrases", [])]
    if extra_text.strip():
        phrases.insert(0, f"{extra_text.strip()[:80]} near {area}")
    providers = ls.make_providers(settings, fetcher)
    seen = set()
    for ph in phrases[: int(settings.get("max_web_queries") or 4)]:
        q = {"q": ph, "lang": "en", "lang_name": "English"}
        out["queries"].append(ph)
        r = ls.web_search_one(q, providers, cache)
        out["errors"].extend(dict(e, query=ph) for e in r["errors"])
        for row in r["results"]:
            if row["url"] not in seen:
                seen.add(row["url"])
                out["web"].append(row)
    tags: List[str] = card_search.get("osm_tags", [])
    if loc and tags:
        radius_m = max(500, min(int(radius_m), 15000))
        around = f"(around:{radius_m},{loc['lat']:.6f},{loc['lon']:.6f})"
        parts = "".join(f'nwr{around}["{k}"="{v}"];' for k, v in (t.split("=", 1) for t in tags))
        query = "[out:json][timeout:25];(" + parts + ");out center tags 60;"
        out["map_query"] = query
        try:
            _, _, raw = fetcher(ls.OVERPASS_URLS[0], method="POST", data=urllib.parse.urlencode({"data": query}).encode(),
                                headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=40)
            out["map"] = ls.parse_overpass(json.loads(raw.decode("utf-8")), loc["lat"], loc["lon"], ls.now_iso())
            if not out["map"]:
                out["notes"].append(f"OpenStreetMap has nothing tagged {', '.join(tags)} within {radius_m / 1000:.1f} km.")
        except ls.NetError as e:
            out["errors"].append({"provider": "OpenStreetMap (Overpass)", "kind": e.kind, "message": str(e)})
        except ValueError:
            out["errors"].append({"provider": "OpenStreetMap (Overpass)", "kind": "bad_data", "message": "Unexpected answer."})
    elif not loc:
        out["notes"].append("Add the shop's postcode to search the map.")
    out["finished_at"] = ls.now_iso()
    return out
