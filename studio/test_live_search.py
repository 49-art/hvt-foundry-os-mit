"""Live search tests with a FAKE network (no real internet used).  python3 -m pytest studio/test_live_search.py -q"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import communities  # noqa: E402
import live_search as ls  # noqa: E402
from netutil import NetError  # noqa: E402

PC = {"status": 200, "result": {"postcode": "HA3 5AA", "latitude": 51.590353, "longitude": -0.332695,
                                "admin_district": "Harrow", "admin_ward": "Marlborough", "region": "London", "country": "England"}}
OVP = {"elements": [
    {"type": "node", "id": 1, "lat": 51.5905, "lon": -0.3330, "tags": {"name": "Al Murad Shop", "shop": "wholesale"}},
    {"type": "node", "id": 2, "lat": 51.6050, "lon": -0.3000, "tags": {"name": "Magazin Românesc", "shop": "convenience",
                                                                     "addr:street": "High Road", "addr:housenumber": "5", "phone": "+44 20 0000 0000"}},
    {"type": "way", "id": 3, "center": {"lat": 51.60, "lon": -0.31}, "tags": {"shop": "wholesale"}},     # no name -> skipped
]}
BRAVE = {"web": {"results": [{"title": "<strong>Romanian</strong> wholesaler", "url": "https://example.org/a", "description": "Food &amp; drink"}]}}
DDG_OK = ('<div class="result"><a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fx&rut=1">Polski '
          'hurtownia</a><a class="result__snippet">Hurtownia w Londynie</a></div>'
          '<a class="result__a" href="https://duckduckgo.com/y.js?ad=1">Advert</a>')
DDG_BLOCK = "<html><body>If this persists, please email us. anomaly detected</body></html>"


class Fake:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def __call__(self, url, method="GET", headers=None, data=None, timeout=20, contact=""):
        self.calls.append({"url": url, "method": method, "headers": headers or {}, "data": data})
        for key, resp in self.routes.items():
            if key in url:
                if isinstance(resp, Exception):
                    raise resp
                body = resp if isinstance(resp, (bytes, str)) else json.dumps(resp)
                return 200, {}, body.encode() if isinstance(body, str) else body
        raise NetError("http", "no route " + url, 404)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(ls.time, "sleep", lambda s: None)


def test_queries_include_native_scripts_and_flag_unchecked_phrases():
    for com, lang, sample in (("romanian", "ro", "â"), ("polish", "pl", "ł"), ("arabic", "ar", "ب"), ("ukrainian", "uk", "о")):
        qs = communities.build_queries(com, "suppliers", "Harrow", True, "")
        native = [q for q in qs if q["lang"] == lang]
        assert native, com
        assert any(sample in q["q"] for q in native) or com == "polish"
        assert all(q["checked_by_native_speaker"] is False for q in native)
        assert any(q["lang"] == "en" for q in qs)
    ar = communities.build_queries("arabic", "stock", "Harrow", True, "")
    assert all(q["dir"] == "rtl" for q in ar if q["lang"] == "ar")


def test_free_text_is_used_and_other_needs_text():
    qs = communities.build_queries("other", "other", "Harrow", True, "chest freezer")
    assert any("chest freezer" in q["q"] for q in qs)
    with pytest.raises(ValueError):
        ls.run_search({"category": "other", "community": "other"}, {}, None, Fake({}))


def test_postcode_lookup_and_bad_postcode():
    f = Fake({"postcodes.io": PC})
    loc = ls.lookup_postcode("ha35aa", f)
    assert loc["area"] == "Harrow" and loc["in_london"] and loc["source_url"].startswith("https://api.postcodes.io/")
    with pytest.raises(NetError):
        ls.lookup_postcode("not a postcode", f)


def test_overpass_query_limits_community_names_to_food_shops():
    q = ls.build_overpass_query("suppliers", 51.59, -0.33, 3000, "roman")
    assert '["name"~"roman",i]' in q and '["shop"~"^(supermarket' in q
    assert "cash ?(and|&|n) ?carry" in q and '["shop"]["name"~"cash' not in q      # no bathroom "cash & carry"
    assert ls.build_overpass_query("other", 51.59, -0.33, 3000, "") == ""


def test_parse_overpass_distances_links_labels():
    rows = ls.parse_overpass(OVP, 51.590353, -0.332695, "2026-09-26T08:00:00+01:00", "rom[aâ]n")
    assert [r["title"] for r in rows] == ["Al Murad Shop", "Magazin Românesc"]
    assert rows[0]["url"] == "https://www.openstreetmap.org/node/1" and rows[0]["distance_m"] < 100
    assert rows[1]["community_match"] is True and "5 High Road" in rows[1]["address"]
    assert all(r["label"] == ls.LABEL and r["checked_at"] for r in rows)


def test_brave_serpapi_ddg_parsers():
    assert ls.parse_brave(BRAVE)[0] == {"title": "Romanian wholesaler", "url": "https://example.org/a", "snippet": "Food & drink", "age": None}
    assert ls.parse_serpapi({"organic_results": [{"title": "t", "link": "https://x.org", "snippet": "s"}]})[0]["url"] == "https://x.org"
    with pytest.raises(NetError):
        ls.parse_serpapi({"error": "Invalid API key"})
    rows = ls.parse_duckduckgo(DDG_OK)
    assert rows == [{"title": "Polski hurtownia", "url": "https://example.com/x", "snippet": "Hurtownia w Londynie"}]
    with pytest.raises(NetError) as e:
        ls.parse_duckduckgo(DDG_BLOCK)
    assert e.value.kind == "blocked"


def test_brave_sends_key_header_and_is_skipped_without_key():
    f = Fake({"api.search.brave.com": BRAVE})
    assert ls.BraveProvider("KEY123", f).search("x")[0]["url"] == "https://example.org/a"
    assert f.calls[0]["headers"]["X-Subscription-Token"] == "KEY123"
    names = [p.name for p in ls.make_providers({"provider_order": ["brave", "serpapi", "duckduckgo"]}, f)]
    assert names == ["duckduckgo"]


def test_full_run_with_ddg_blocked_still_returns_map_and_clear_message(tmp_path):
    f = Fake({"postcodes.io": PC, "overpass": OVP, "duckduckgo": DDG_BLOCK})
    r = ls.run_search({"category": "suppliers", "community": "romanian", "postcode": "HA3 5AA", "radius_m": 3000},
                      {"max_web_queries": 3}, ls.Cache(tmp_path / "c.json"), f)
    assert r["location"]["area"] == "Harrow" and len(r["map"]) == 2 and r["web"] == []
    assert any(e["kind"] == "blocked" for e in r["errors"]) and r["notes"]
    assert sum(q["used"] for q in r["queries"]) == 3
    assert any(q["lang"] == "ro" and q["used"] for q in r["queries"])     # native phrases are really searched


def test_full_run_with_brave_key_gives_web_results_with_source_and_date(tmp_path):
    f = Fake({"postcodes.io": PC, "overpass": OVP, "api.search.brave.com": BRAVE})
    r = ls.run_search({"category": "stock", "community": "polish", "postcode": "HA3 5AA"},
                      {"brave_api_key": "k", "provider_order": ["brave"], "max_web_queries": 2}, None, f)
    w = r["web"][0]
    assert w["source"] == "web (Brave Search)" and w["checked_at"] and w["label"] == ls.LABEL and w["query"]


def test_cache_prevents_repeat_calls(tmp_path):
    c = ls.Cache(tmp_path / "c.json")
    f = Fake({"postcodes.io": PC})
    ls.lookup_postcode("HA3 5AA", f, c)
    again = ls.lookup_postcode("HA3 5AA", f, c)
    assert len(f.calls) == 1 and again["cached"] is True


def test_offline_is_reported_plainly_and_stops_web(tmp_path):
    off = NetError("offline", "No internet connection.")
    f = Fake({"postcodes.io": off, "overpass": off, "duckduckgo": off})
    r = ls.run_search({"category": "finance", "community": "turkish", "postcode": "HA3 5AA"}, {}, None, f)
    assert r["map"] == [] and r["web"] == [] and any(e["kind"] == "offline" for e in r["errors"])
    assert sum(1 for c in f.calls if "duckduckgo" in c["url"]) <= 1


def test_overpass_falls_back_to_next_server():
    calls = {"n": 0}

    def f(url, **kw):
        calls["n"] += 1
        if calls["n"] < 3:
            raise NetError("http", "504 busy", 504)
        return 200, {}, json.dumps(OVP).encode()
    loc = {"lat": 51.590353, "lon": -0.332695}
    r = ls.search_map("suppliers", loc, 3000, "", f)
    assert r["endpoint"] == ls.OVERPASS_URLS[2] and len(r["results"]) == 2


def test_one_service_dropping_us_is_not_called_offline():
    off = NetError("offline", "No internet connection.")
    f = Fake({"postcodes.io": PC, "overpass": OVP, "duckduckgo": off})
    r = ls.run_search({"category": "stock", "community": "polish", "postcode": "HA3 5AA"}, {"max_web_queries": 2}, None, f)
    assert all(e["kind"] == "connection" for e in r["errors"]) and "offline" not in " ".join(r["notes"])
