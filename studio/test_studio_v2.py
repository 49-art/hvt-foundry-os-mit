"""Studio v0.2: live search, saved finds, shop apps, connectors, settings — through the kernel, with a FAKE network.
python3 -m pytest studio/test_studio_v2.py -q"""
import json
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_search  # noqa: E402
from studio_core import Studio, StudioRefusal, STUDIO_AUTHORITY  # noqa: E402
OPTIONAL_ACTIONS = STUDIO_AUTHORITY["Architecture Office"]
from app import make_server  # noqa: E402

PC = {"result": {"postcode": "HA3 5AA", "latitude": 51.590353, "longitude": -0.332695, "admin_district": "Harrow", "region": "London"}}
OVP = {"elements": [{"type": "node", "id": 9492463841, "lat": 51.5906, "lon": -0.3330, "tags": {"name": "Al Murad Shop", "shop": "wholesale"}}]}
NEW_ACTIONS = ("run_live_search", "save_search_result", "build_shop_app", "export_shop_app", "update_studio_settings", "manage_connector")


def fake(url, method="GET", headers=None, data=None, timeout=20, contact=""):
    if "postcodes.io" in url:
        return 200, {}, json.dumps(PC).encode()
    if "overpass" in url:
        return 200, {}, json.dumps(OVP).encode()
    if "duckduckgo" in url:
        return 202, {}, b"<html>anomaly</html>"
    if "frankfurter" in url:
        return 200, {}, json.dumps({"amount": 1, "base": "GBP", "date": "2026-09-25", "rates": {"EUR": 1.1622}}).encode()
    return 200, {}, b"{}"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(live_search.time, "sleep", lambda s: None)


@pytest.fixture
def st(tmp_path):
    return Studio(state_path=tmp_path / "state.json", fetcher=fake)


def test_new_actions_are_in_the_studio_map_and_draft():
    # Updated 18 Oct 2026 (DR-2026-10-18-01): these six actions were "Draft"; the founder approved
    # them as interim. The label must now say so AND still say the Chief Architect review is owed.
    for a in NEW_ACTIONS:
        assert a in OPTIONAL_ACTIONS and "DR-2026-09-26-08" in OPTIONAL_ACTIONS[a]
        # Amended 20 Nov 2026 (DR-2026-11-20-11 / -12): approved; Chief Architect review done by the
        # CEO Office under EXC-2026-11-20-01. Was: "founder-approved interim" and
        # "pending Chief Architect review" in the label.
        assert "Approved — DR-2026-11-20-11" in OPTIONAL_ACTIONS[a] and "EXC-2026-11-20-01" in OPTIONAL_ACTIONS[a]


def test_new_actions_refused_for_ceo_agent(st):
    for a in NEW_ACTIONS:
        with pytest.raises(StudioRefusal) as e:
            st._authorize(a, {}, agent="AGT-0001")
        assert e.value.code == 403
    assert sum(1 for ev in st.store.data["events"] if ev["outcome"] == "refused") == len(NEW_ACTIONS)


def test_search_save_build_export_loop(st):
    sid = st.open_session("BUT-0002", business_name="Test grocer")["result"]["id"]
    r = st.live_search({"category": "suppliers", "community": "romanian", "postcode": "HA3 5AA", "session_id": sid})
    assert r["kernel"]["status"] == "pending_human_review" and r["map"][0]["title"] == "Al Murad Shop"
    assert any(e["kind"] == "blocked" for e in r["errors"])
    with pytest.raises(StudioRefusal):
        st.save_search_result(sid, {"title": "x", "url": "https://x.org"})               # no checked date -> refused
    with pytest.raises(StudioRefusal):
        st.save_search_result(sid, {"title": "x", "url": "javascript:alert(1)", "checked_at": "now"})
    f = st.save_search_result(sid, r["map"][0])["result"]
    assert f["id"].startswith("FND-") and f["verified"] is False and f["label"] == live_search.LABEL
    assert st.save_search_result(sid, r["map"][0])["result"]["id"] == f["id"]            # no duplicates
    with pytest.raises(StudioRefusal):
        st.build_shop_app(sid, {"name": "Test grocer"})                                  # needs owner password
    b = st.build_shop_app(sid, {"name": "Test grocer", "languages": ["ro", "en"], "postcode": "HA3 5AA"}, "owner-pass")["result"]
    assert "password_hash" not in json.dumps(b) and b["preview_url"].startswith("/shops/")
    site = st.shop_site_dir(b["folder"])
    assert "Al Murad" not in (site / "content.json").read_text(encoding="utf-8")         # suppliers stay private
    ex = st.export_shop_app(sid)["result"]
    names = zipfile.ZipFile(ex["zip"]).namelist()
    assert any(n.endswith("site/manifest.webmanifest") for n in names) and not any("secrets" in n for n in names)
    assert st.shop_app_draft(sid)["shop"]["suppliers_count"] == 1
    assert st.session_detail(sid)["saved_results"][0]["title"] == "Al Murad Shop"


def test_settings_are_masked_and_names_only_logged(st):
    st.save_settings({"brave_api_key": "BSA_SECRET_1234567", "max_web_queries": 99, "provider_order": ["nope"]})
    pub = st.get_settings()
    assert pub["brave_api_key"] == "••••4567" and pub["max_web_queries"] == 12 and pub["provider_order"] == ["brave", "serpapi", "duckduckgo"]
    st.save_settings({"brave_api_key": "••••4567"})
    assert st.settings.load()["brave_api_key"] == "BSA_SECRET_1234567"
    assert "BSA_SECRET" not in json.dumps(st.store.data)


def test_connectors_per_scope(st):
    sid = st.open_session("BUT-0003")["result"]["id"]
    st.connector_op(sid, "stripe", "credentials", {"values": {"secret_key": "sk_test_SCOPED9999"}})
    assert st.connectors_list(sid)["counts"]["working-tested"] >= 5
    shop_items = {c["id"]: c for c in st.connectors_list(sid)["items"]}
    studio_items = {c["id"]: c for c in st.connectors_list("studio")["items"]}
    assert shop_items["stripe"]["saved_credentials"] == {"secret_key": "••••9999"} and studio_items["stripe"]["saved_credentials"] == {}
    assert st.connector_op("studio", "frankfurter", "test", {})["result"]["ok"] is True
    with pytest.raises(StudioRefusal):
        st.connector_op("../../x", "stripe", "test", {})
    assert "sk_test_SCOPED" not in json.dumps(st.store.data)


@pytest.fixture
def server(tmp_path):
    httpd, studio = make_server("127.0.0.1", 0, tmp_path / "http.json", fetcher=fake)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", studio
    httpd.shutdown(); httpd.server_close()


def call(base, path, body=None, cookie=""):
    req = urllib.request.Request(base + path, method="POST" if body is not None else "GET",
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", "Cookie": cookie})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if "json" in r.headers["Content-Type"] else raw), r.headers
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), e.headers


def test_http_new_routes(server):
    base, _ = server
    assert call(base, "/api/communities")[1]["categories"]["storage"]
    qs = call(base, "/api/queries?community=arabic&category=stock")[1]
    assert any(q["dir"] == "rtl" for q in qs)
    sid = call(base, "/api/sessions", {"business_type_id": "BUT-0002", "business_name": "G"})[1]["result"]["id"]
    r = call(base, "/api/search", {"category": "delivery", "community": "polish", "postcode": "HA3 5AA", "session_id": sid})[1]
    assert r["location"]["area"] == "Harrow"
    assert call(base, f"/api/sessions/{sid}/save-result", {"result": r["map"][0]})[0] == 200
    assert call(base, f"/api/sessions/{sid}/shop-app", {"shop": {"name": "G shop", "languages": ["pl", "en"]}, "password": "owner-pass"})[0] == 200
    ex = call(base, f"/api/sessions/{sid}/shop-app/export", {})[1]["result"]
    code, blob, h = call(base, ex["download_url"])
    assert code == 200 and blob[:2] == b"PK"
    folder = call(base, f"/api/sessions/{sid}/shop-app")[1]["record"]["folder"]
    code, html, _ = call(base, f"/shops/{folder}/")
    assert code == 200 and b'lang="pl"' in html
    assert call(base, "/api/exports/..%2F..%2Fstate.json")[0] == 404
    assert call(base, "/api/connectors?scope=studio")[1]["counts"]
    assert call(base, "/api/connectors/frankfurter/test", {"scope": "studio"})[1]["result"]["ok"] is True
    o = call(base, "/api/connectors/custom_api/openapi", {"scope": "studio", "spec": json.dumps(
        {"openapi": "3.0.0", "info": {"title": "T"}, "servers": [{"url": "https://api.frankfurter.dev/v1"}], "paths": {"/latest": {"get": {}}}})})[1]
    assert o["result"]["endpoints"][0]["path"] == "/latest"
    assert call(base, "/api/connectors/custom_api/custom", {"scope": "studio", "slug": "fx", "definition": {
        "base_url": "https://api.frankfurter.dev/v1", "actions": [{"name": "latest", "method": "GET", "path": "/latest"}]}})[0] == 200
    assert call(base, "/api/connectors/custom:fx/run", {"scope": "studio", "action": "latest"})[1]["result"]["result"]["json"]["rates"]


def test_http_studio_password_gate(server):
    base, _ = server
    assert call(base, "/api/auth-status")[1]["password_set"] is False
    assert call(base, "/api/settings", {"studio_password": "letmein99"})[0] == 200
    assert call(base, "/api/state")[0] == 401
    assert call(base, "/api/login", {"password": "nope"})[0] == 403
    code, _, h = call(base, "/api/login", {"password": "letmein99"})
    cookie = h["Set-Cookie"].split(";")[0]
    assert call(base, "/api/state", cookie=cookie)[0] == 200
