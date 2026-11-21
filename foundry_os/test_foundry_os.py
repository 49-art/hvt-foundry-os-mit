"""Tests for the HVT Foundry OS (ENG-0004 Configurator, Prototype — DR-2026-11-20-11)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from foundry_os import ROOT
from foundry_os.governance import verify
from foundry_os.ladder import Ladder, PENDING

sys.path.insert(0, str(ROOT / "tools"))
from completion_cards_2026_11_20 import complexity  # noqa: E402

MINA = json.loads((Path(__file__).parent / "examples" / "mina_theatre_SES-0002-F-0001.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def L():
    return Ladder()


def test_mina_theatre_reproduces_filed_record(L):
    r = L.run(MINA)
    assert r["rung1_classify"]["type"] == "BUT-0001"
    probs = {p["id"] for p in r["rung2_problems"]}
    assert probs == {"PRB-0001", "PRB-0002", "PRB-0003", "PRB-0004", "PRB-0006"}  # not PRB-0005: card machine works
    stock = [m for m in r["rung4_match"] if "Stock" in m["capability"]][0]
    assert stock["path"].startswith("DR-10 S3")                       # till is not Square
    assert r["rung7_brand"]["decision"] == "SKIP"
    assert r["rung8_deploy"][0].startswith("Mon") and r["rung8_deploy"][-1].startswith("Fri")
    assert len(r["rung8_deploy"]) == 6
    assert r["rung6_gaps"]["eng_0005_trigger"] is False                # theatre never triggers
    assert r["rung6_gaps"]["wishes"][0]["words_verbatim"] == MINA["wishes"][0]
    assert r["status"] == PENDING and r["authoritative"] is False and r["theatre"] is True


def test_square_owner_gets_s1(L):
    r = L.run(dict(MINA, pos="Square"))
    stock = [m for m in r["rung4_match"] if "Stock" in m["capability"]][0]
    assert stock["path"].startswith("DR-10 S1")


def test_live_two_source_gap_reports_eng_0005_trigger_only(L):
    r = L.run(dict(MINA, live=True, problem_words="Colour in the cupboard and foil in the wholesaler book — two lists, it runs out."))
    assert r["rung6_gaps"]["eng_0005_trigger"] is True
    assert "does not register" in r["rung6_gaps"]["eng_0005_note"]
    assert "ENG-0005" not in L.obj                                      # still not registered


@pytest.mark.parametrize("words,expected", [
    ("Polish deli, pierogi and kielbasa on the import counter", "BUT-0002"),
    ("Halal neighbourhood grocery, families ask who is the supplier", "BUT-0003"),
    ("Fabric shop, I know every weave", "BUT-0004"),
    ("Gifts and household shop on the high street", "BUT-0005"),
    ("Physio clinic, two treatment rooms", "BUT-0006"),
    ("Carpenter and joiner, one van, kitchens and decking", "BUT-0007"),
    ("Barber shop, three chairs", "BUT-0001"),
])
def test_each_card_classifies(L, words, expected):
    assert L.classify(words)["type"] == expected


def test_specific_retail_beats_generic(L):
    c = L.classify("Polish deli shop with a till")
    assert c["type"] == "BUT-0002" and "BUT-0005" not in c["keywords"]


def test_dual_type_grocer_with_trust_rule(L):
    c = L.classify("Polish deli, halal meat counter too, grocery")
    assert {c["type"], *c["also"]} >= {"BUT-0002", "BUT-0003"}


def test_owner_hint_overrides_classification_xiv6(L):
    c = L.classify("Barber shop, three chairs", hint="BUT-0005")
    assert c["type"] == "BUT-0005" and any("XIV.6" in h for h in c["history"])


def test_unknown_business_flags_new_type(L):
    r = L.run({"owner_words": "We run a pet crematorium", "live": False})
    assert r["rung1_classify"]["type"] is None and "new type" in r["rung1_classify"]["flag"]
    assert r["stopped_at"] == "rung 1"


def test_clinic_records_out_of_scope(L):
    r = L.run({"owner_words": "Physio clinic", "wishes": ["Keep my patient notes and clinical records in WhatsApp"],
               "live": False})
    g = r["rung6_gaps"]
    assert any("Clinical / medical records" in x for x in g["out_of_scope_requested"])
    assert g["wishes"][0]["status"] == "Under Review" and g["wishes"][0]["resolution"].startswith("Out of scope")


def test_trust_rule_stored_verbatim_never_certified(L):
    s = "Every chicken here is hand-slaughtered halal from Haji’s, and I check each delivery myself."
    r = L.run({"owner_words": "Halal neighbourhood grocery", "trust_rule": s, "live": False})
    assert r["trust_rule"]["owner_sentence_verbatim"] == s and r["trust_rule"]["certified_by_foundry"] is False


def test_public_surface_requires_brand_and_stan_lee(L):
    r = L.run(dict(MINA, public_surface=True))
    assert r["rung7_brand"]["decision"] == "REQUIRED" and "Stan Lee" in r["rung7_brand"]["stan_lee"]


def test_quote_shows_take_type_only_no_prices(L):
    for t in L.types:
        for q in L.quote(t):
            assert "£" not in json.dumps(q) and "$" not in json.dumps(q)
            assert q["take"]


def test_complexity_scores_match_dr_2026_11_20_08(L):
    want = {"BUT-0001": 2, "BUT-0002": 3, "BUT-0003": 3, "BUT-0004": 2, "BUT-0005": 2, "BUT-0006": 2, "BUT-0007": 2}
    assert {t: L.types[t]["card"]["complexity_score"] for t in want} == want
    for t in want:
        assert complexity(L.types[t]["card"]) == want[t]


def test_governance_verifier_passes():
    r = verify()
    assert r["ok"], r["errors"]
    assert r["constitution_version"] == "1.3" and r["completion_drs"] >= 12


def test_cli_status_and_verify_exit_zero():
    for cmd in ("status", "verify", "cards", "decisions"):
        p = subprocess.run([sys.executable, "-m", "foundry_os", cmd], cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 0, p.stdout + p.stderr
    p = subprocess.run([sys.executable, "-m", "foundry_os", "ladder", "foundry_os/examples/mina_theatre_SES-0002-F-0001.json"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0 and '"BUT-0001"' in p.stdout
