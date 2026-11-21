"""Run REAL live searches and connector tests from this computer and write LIVE_SEARCH_SAMPLE_OUTPUT.txt.
Uses the real internet. No keys are needed; keyed services report 'add key'.   python3 studio/live_sample.py"""
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import connectors as C  # noqa: E402
import live_search as ls  # noqa: E402
from settings import Settings  # noqa: E402

RUNS = [
    ("Romanian grocer — suppliers", {"category": "suppliers", "community": "romanian", "postcode": "HA3 5AA", "radius_m": 5000}),
    ("Polish shop — stock", {"category": "stock", "community": "polish", "postcode": "HA3 5AA", "radius_m": 3000}),
    ("Arabic sweets — stock (baklava)", {"category": "stock", "community": "arabic", "postcode": "HA3 5AA", "radius_m": 3000, "free_text": "baklava"}),
    ("Any shop — storage near Harrow town centre", {"category": "storage", "community": "other", "postcode": "HA1 1AA", "radius_m": 5000}),
    ("Any shop — delivery / couriers", {"category": "delivery", "community": "other", "postcode": "HA3 5AA", "radius_m": 2000}),
    ("Turkish shop — finance", {"category": "finance", "community": "turkish", "postcode": "HA3 5AA", "radius_m": 1500}),
]


def main():
    out = []
    w = out.append
    tmp = Path(tempfile.mkdtemp())
    settings = Settings(tmp / "settings.json").load()          # empty settings: no Brave key, like a fresh install
    w(f"HVT Foundry Studio — LIVE sample run, {datetime.now().astimezone().isoformat(timespec='seconds')} (box clock, Europe/London)")
    w("Real internet from the build box. No Brave/SerpAPI key. Fresh cache (nothing re-used). Nothing here is checked by us.")
    w("Provider order: " + ", ".join(settings["provider_order"]) + f"; max web queries per search: {settings['max_web_queries']}")
    for title, params in RUNS:
        w("\n" + "=" * 100 + f"\n{title}\n  params: {params}")
        t0 = time.time()
        r = ls.run_search(params, settings, ls.Cache(tmp / "cache.json"))
        w(f"  took {time.time() - t0:.1f}s")
        if r["location"]:
            L = r["location"]
            w(f"  location: {L['postcode']} = {L['ward']}, {L['area']} ({L['lat']}, {L['lon']}) — {L['source_url']} checked {L['checked_at']}")
        w("  phrases used for web search:")
        for q in r["queries"]:
            if q["used"]:
                w(f"    [{q['lang_name']}] {q['q']}" + ("   (not yet checked by a native speaker)" if not q["checked_by_native_speaker"] else ""))
        w(f"  WEB results: {len(r['web'])}")
        for x in r["web"][:8]:
            w(f"    - {x['title']} | {x['url']} | via {x['source']} | query lang {x['query_lang']} | checked {x['checked_at']}")
        w(f"  MAP results (OpenStreetMap): {len(r['map'])}" + (f"  endpoint note: {r.get('map_query', '')[:0]}" if False else ""))
        for x in r["map"][:12]:
            w(f"    - {x['title']} ({x['kind']}) — {x['distance_text']} — {x['address']} | {x['url']}"
              + (" | COMMUNITY NAME MATCH" if x["community_match"] else "") + f" | checked {x['checked_at']}")
        seen = set()
        for e in r["errors"]:
            k = (e["provider"], e["message"])
            if k not in seen:
                seen.add(k)
                w(f"  ERROR from {e['provider']} ({e['kind']}): {e['message']}")
        for n in r["notes"]:
            w(f"  NOTE: {n}")
        time.sleep(4)                                            # be polite to the free services
    w("\n" + "=" * 100 + "\nCONNECTOR 'Test' buttons, run live now (no keys added):")
    for cid, cls in sorted(C.registry().items()):
        if cid == "custom_api":
            continue
        creds = {"phone": "07700900123"} if cid == "whatsapp_link" else {}
        r = C._safe_test(cls(creds))
        w(f"  {cid:24s} [{cls.status:21s}] {'OK ' if r['ok'] else 'NO '} {r['message']}")
    cm_def = {"label": "Frankfurter (custom)", "base_url": "https://api.frankfurter.dev/v1",
              "actions": [{"name": "latest", "method": "GET", "path": "/latest"}]}
    r = C.custom_api.CustomAPI({}, definition=cm_def, slug="fx").run("latest", {"base": "GBP", "symbols": "RON,PLN,EUR,TRY"})
    w(f"  custom API (frankfurter v1 /latest, GBP): HTTP {r['status']} -> {r.get('json', r.get('text'))}")
    try:
        from netutil import fetch_json
        spec = fetch_json("https://api.frankfurter.dev/v2/openapi.json")
        o = C.custom_api.parse_openapi(spec)
        w(f"  OpenAPI import of https://api.frankfurter.dev/v2/openapi.json: '{o['title']}' base {o['base_url']} — {len(o['endpoints'])} endpoints: "
          + ", ".join(f"{e['method']} {e['path']}" for e in o["endpoints"]))
    except Exception as e:  # report, don't hide
        w(f"  OpenAPI import failed: {e}")
    (HERE / "LIVE_SEARCH_SAMPLE_OUTPUT.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
