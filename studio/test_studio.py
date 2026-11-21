"""Tests for HVT Foundry Studio. Run from the repo root:  python3 -m pytest studio/test_studio.py -v"""
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio_core import Studio, StudioRefusal  # noqa: E402
import factcheck  # noqa: E402
from app import make_server  # noqa: E402


@pytest.fixture
def st(tmp_path):
    return Studio(state_path=tmp_path / "state.json")


def _session(st, but="BUT-0001"):
    return st.open_session(but, business_name="test")["result"]["id"]


# ---- boot ---------------------------------------------------------------------
def test_boot_runs_four_gates_and_three_refusals(st):
    assert st.booted
    outcomes = [(s["gate"], s["outcome"]) for s in st.boot_steps]
    assert ("1", "pass") in outcomes and ("2", "pass") in outcomes
    assert sum(1 for s in st.boot_steps if s["outcome"] == "refused") == 3
    assert all(s["as_expected"] for s in st.boot_steps)


def test_boot_fails_closed_with_draft_constitution(tmp_path):
    bad = tmp_path / "c.md"
    bad.write_text("Document ID: HVT-0001\nTitle: X\nVersion: 1.2\nStatus: Draft\n", encoding="utf-8")
    s = Studio(state_path=tmp_path / "s.json", constitution=bad)
    assert not s.booted
    with pytest.raises(StudioRefusal) as e:
        s.open_session("BUT-0001")
    assert e.value.code == 503
    assert any(a["outcome"] == "refused" for a in s.store.data["audit"])


# ---- step 1-2 -------------------------------------------------------------------
def test_open_session_mints_ids_after_reserved_ones(st):
    r = st.open_session("BUT-0001")
    assert r["result"]["id"] == "SES-0004"                     # SES-0001..0003 exist in the record
    assert r["review_status"] == "pending_human_review"
    assert "Studio action map" in r["kernel"]["authorized_by"]
    assert st.open_session("BUT-0002")["result"]["id"] == "SES-0005"


def test_open_session_refuses_non_business_type(st):
    with pytest.raises(StudioRefusal):
        st.open_session("ENG-0003")


def test_owner_correction_overrides_and_keeps_history(st):
    sid = _session(st)
    st.classify(sid, business_type_id="BUT-0005", owner_words="We're really a shop")
    s = st.store.get("sessions", sid)
    assert s["classification"]["business_type_id"] == "BUT-0005"
    assert s["classification"]["source"] == "owner-corrected"
    assert s["classification"]["owner_corrections"][0]["owner_words"] == "We're really a shop"
    assert [h["rev"] for h in st.store.history("sessions", sid)] == [1, 2]


def test_unlisted_business_gives_honest_empty_configuration(st):
    sid = _session(st)
    st.classify(sid, business_type_id="UNLISTED", owner_words="mobile dog groomer")
    cfg = st.run_configurator(sid)["result"]["configuration"]
    assert cfg["known"] is False and cfg["engines"] == [] and cfg["components"] == []


# ---- step 3 configurator -------------------------------------------------------
def test_configurator_uses_only_graph_data_for_hair_salon(st):
    cfg = st.configurator("BUT-0001", "2–5 Staff", "£0–50", "Basic")
    assert [e["id"] for e in cfg["engines"]] == ["ENG-0001", "ENG-0002", "ENG-0003"]
    assert {c["id"] for c in cfg["components"]} == {f"SLC-000{i}" for i in range(1, 9)}
    stock = [c for c in cfg["capabilities"] if c["name"].startswith("Stock")][0]
    assert stock["covered_by"] is None and stock["overlay"]["search_result"] == "PARTIAL MATCH"
    assert not any(e["id"] in ("ENG-0005", "ENG-0006") for e in cfg["engines"])
    assert [p for p in cfg["problems"] if p["id"] == "PRB-0004"][0]["solved_by"] == []


def test_unverified_vendor_facts_are_flagged_not_hidden(st):
    cfg = st.configurator("BUT-0001", None, "£0–50", None)
    qb = [c for c in cfg["components"] if c["name"] == "QuickBooks"][0]
    assert qb["factcheck"]["overall"] == "unverified" and qb["budget_fit"] == "unknown"
    ap = [c for c in cfg["components"] if c["name"] == "Apple Pay"][0]
    assert any(f["result"] == "mismatch" and "101" in f["note"] for f in ap["factcheck"]["fields"])


def test_budget_filter_uses_verified_prices_and_size_tech_are_not_faked(st):
    cfg = st.configurator("BUT-0001", "1 Person", "£0–50", "None")
    xero = [c for c in cfg["components"] if c["name"] == "Xero"][0]
    assert xero["budget_fit"] == "fits" and factcheck.FACTCHECK["SLC-0006"]["min_monthly_gbp"] == 18
    assert cfg["filters"]["size"]["applied"] is False and cfg["filters"]["tech"]["applied"] is False


def test_card_summary_type_shows_gaps_honestly(st):
    # Amended 20 Nov 2026 (DR-2026-11-20-10 / -12): BUT-0006 is now an Approved full card, so the
    # "card-summary / pending Raj + Stan Lee" state no longer exists. Gaps must still be honest.
    # Was: cfg["data_level"] == "card-summary" and cfg["components"] == []
    # Was: any("pending Raj + Stan Lee" in g for g in types["BUT-0006"]["gaps"])
    cfg = st.configurator("BUT-0006", None, None, None)
    assert cfg["data_level"] == "full"
    types = {t["id"]: t for t in st.business_types()}
    gaps = types["BUT-0006"]["gaps"]
    assert any("Out of scope" in g for g in gaps)          # clinical records stay out of scope
    assert any("Stan Lee veto" in g for g in gaps)         # design veto deferred, not waived
    assert not any("pending" in g for g in gaps)
    assert st.card_markdown("BUT-0006")


def test_invalid_sizing_value_refused(st):
    sid = _session(st)
    with pytest.raises(StudioRefusal):
        st.run_configurator(sid, size="Huge")


# ---- steps 4-6 ----------------------------------------------------------------
def test_plain_package_and_owner_response_is_not_a_foundry_approval(st):
    sid = _session(st)
    p = st.run_configurator(sid, budget="£0–50")["result"]
    heads = " ".join(l["head"] for l in p["plain"])
    assert "Knowing when stock is low" in heads and "Your data stays yours" in heads
    r = st.record_owner_response(sid, p["id"], "accept", "fine")["result"]
    assert "not a Foundry approval" in r["meaning"]
    assert "pending Foundry human review" in st.store.get("proposals", p["id"])["status"]
    statuses = [r.get("status", "") for recs in st.store.data["records"].values() for r in recs]
    assert not any(x.startswith("Approved") for x in statuses)


def test_wish_keeps_owner_words_verbatim_and_requires_words(st):
    sid = _session(st)
    words = "tell me when the COLOUR's running low!!"
    w = st.capture_wish(sid, words, priority="Must", customer_asset_flag=True)["result"]
    assert w["id"] == "WSH-0002" and w["description"] == words and w["status"] == "Logged"
    with pytest.raises(StudioRefusal):
        st.capture_wish(sid, "   ")


def test_closed_session_is_permanent(st):
    sid = _session(st)
    st.close_session(sid)
    for fn in (lambda: st.capture_wish(sid, "x"), lambda: st.classify(sid, owner_words="x"),
               lambda: st.close_session(sid)):
        with pytest.raises(StudioRefusal) as e:
            fn()
        assert e.value.code == 409


# ---- step 7-8 return path ------------------------------------------------------
def test_return_path_three_outcomes_nothing_deleted(st):
    sid = _session(st)
    w1 = st.capture_wish(sid, "stock alerts")["result"]["id"]
    w2 = st.capture_wish(sid, "gift cards online")["result"]["id"]
    w3 = st.capture_wish(sid, "do my accounts")["result"]["id"]
    with pytest.raises(StudioRefusal):                     # session still open
        st.resolve_wish(w1, "reconfigure", "x")
    st.close_session(sid)
    assert {w["id"] for w in st.review_queue()} == {w1, w2, w3}
    a = st.resolve_wish(w1, "reconfigure", "Square alerts (DOC-0006 S1)")
    b = st.resolve_wish(w2, "engine_search", "no engine", "Gift cards")
    c = st.resolve_wish(w3, "out_of_scope", "owner's accountant")
    assert a["result"]["status"] == "Configured" and a["kernel"]["action"] == "resolve_wish"
    assert b["result"]["status"] == "Engine Search Required" and b["kernel"]["action"] == "run_engine_search"
    assert "Out of scope" in c["result"]["resolution"]
    assert st.review_queue() == []
    assert st.store.get("sessions", sid)["status"] == "Actioned"
    assert [r["status"] for r in st.wish_history(w1)] == ["Logged", "Configured"]
    assert len(st.store.data["records"]["wishes"]) == 6        # 3 originals + 3 superseding revisions
    with pytest.raises(StudioRefusal):
        st.resolve_wish(w1, "out_of_scope", "again")
    with pytest.raises(StudioRefusal):
        st.resolve_wish(w3, "engine_search", "")


def test_follow_up_offers_new_configuration_and_carries_owner_answer(st):
    sid = _session(st)
    w = st.capture_wish(sid, "stock alerts")["result"]["id"]
    st.close_session(sid)
    st.resolve_wish(w, "reconfigure", "Square alerts")
    f = st.offer_follow_up(sid)["result"]
    assert f["follow_up_of"] == sid and f["carried_wishes"] == [w] and f["status"] == "Open"
    p = st.run_configurator(f["id"])["result"]
    st.record_owner_response(f["id"], p["id"], "accept")
    assert st.store.get("wishes", w)["status"] == "Accepted"


# ---- authority + audit + persistence -------------------------------------------
def test_every_action_is_kernel_checked_and_refusals_are_logged(st):
    sid = _session(st)
    st.capture_wish(sid, "x")
    assert all(e["kernel"]["status"] == "pending_human_review" for e in st.store.data["events"] if e["outcome"] == "ok")
    for case in ("ceo_captures_wish", "architect_amends_constitution", "architect_approves_governance_doc"):
        assert st.authority_test(case)["refused"] is True
    assert sum(1 for e in st.store.data["events"] if e["outcome"] == "refused") == 3
    gates = {a["gate"] for a in st.store.data["audit"]}
    assert {"constitution", "graph", "agent_registration", "workflow_authority", "boot_order"} <= gates


def test_state_persists_across_restart(tmp_path):
    p = tmp_path / "state.json"
    a = Studio(state_path=p)
    sid = a.open_session("BUT-0001")["result"]["id"]
    a.capture_wish(sid, "keep me")
    b = Studio(state_path=p)
    assert b.store.get("sessions", sid)["linked_wishes"] == ["WSH-0002"]
    assert b.open_session("BUT-0001")["result"]["id"] == "SES-0005"


def test_studio_never_writes_governance_or_graph(st):
    root = Path(__file__).resolve().parent.parent
    before = (root / "graph" / "foundry_graph.json").read_bytes()
    sid = _session(st); st.capture_wish(sid, "x"); st.close_session(sid)
    assert (root / "graph" / "foundry_graph.json").read_bytes() == before


# ---- HTTP ---------------------------------------------------------------------
@pytest.fixture
def server(tmp_path):
    httpd, studio = make_server("127.0.0.1", 0, tmp_path / "http.json")
    t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown(); httpd.server_close()


def call(base, path, body=None):
    req = urllib.request.Request(base + path, method="POST" if body is not None else "GET",
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read()) if "json" in r.headers["Content-Type"] else r.read()
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_http_full_loop(server):
    assert call(server, "/api/boot", {})[1]["ok"] is True
    code, html = call(server, "/")
    assert code == 200 and b"HVT Foundry Studio" in html
    sid = call(server, "/api/sessions", {"business_type_id": "BUT-0001"})[1]["result"]["id"]
    call(server, f"/api/sessions/{sid}/classify", {"owner_words": "also nails"})
    p = call(server, f"/api/sessions/{sid}/configure", {"budget": "£0–50"})[1]["result"]["id"]
    assert call(server, f"/api/sessions/{sid}/response", {"proposal_id": p, "decision": "reject"})[0] == 200
    w = call(server, f"/api/sessions/{sid}/wishes", {"description": "stock on phone"})[1]["result"]["id"]
    assert call(server, f"/api/sessions/{sid}/close", {})[1]["result"]["status"] == "Closed"
    assert [x["id"] for x in call(server, "/api/queue")[1]] == [w]
    r = call(server, f"/api/wishes/{w}/resolve", {"outcome": "engine_search", "reason": "r", "capability": "stock"})[1]
    assert r["review_status"] == "pending_human_review"
    audit = call(server, "/api/audit")[1]
    assert len(audit["studio_events"]) == 7 and audit["kernel_audit"]


def test_http_refusals_have_codes(server):
    assert call(server, "/api/sessions", {"business_type_id": "ENG-0001"})[0] == 400
    assert call(server, "/api/sessions/SES-9999")[0] == 404
    t = call(server, "/api/authority-test", {"case": "ceo_captures_wish"})[1]
    assert t["refused"] is True
    assert call(server, "/api/nope")[0] == 404
