"""Tests for the Foundry Kernel (HVT-0005). Run: cd kernel && python3 -m pytest test_kernel.py -v"""
import json
from pathlib import Path

import pytest

from foundry_kernel import (FoundryKernel, BootOrderError, ConstitutionError, GraphError,
                            AgentRegistrationError, UnauthorizedActionError, KernelRefusal,
                            parse_metadata_header)

ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION = ROOT / "governance" / "HVT-0001_Constitution.md"
GRAPH = ROOT / "graph" / "foundry_graph.json"


def write_constitution(tmp_path, status="Approved", doc_id="HVT-0001"):
    p = tmp_path / "c.md"
    p.write_text(f"Document ID: {doc_id}\nTitle: HVT Foundry Constitution\nVersion: 1.2\n"
                 f"Status: {status}\nOwner: CEO Agent\nReviewed By: Chief Architect\n"
                 "Dependencies: None\n\n---\n\n# body\n", encoding="utf-8")
    return p


def write_graph(tmp_path, objects):
    p = tmp_path / "g.json"
    p.write_text(json.dumps({"objects": objects}), encoding="utf-8")
    return p


def mk(id, cls="Document", status="Draft", rels=None, **kw):
    o = {"id": id, "class": cls, "name": id, "owner": "Architecture Office", "status": status,
         "version": "0.1", "relationships": rels or [], "authority": "test"}
    o.update(kw)
    return o


@pytest.fixture
def booted():
    k = FoundryKernel()
    k.load_constitution(CONSTITUTION)
    k.load_graph(GRAPH)
    return k


@pytest.fixture
def with_agents(booted):
    booted.register_agent("AGT-0001")
    booted.register_agent("AGT-0002")
    return booted


# ---- Gate 1: Constitution ---------------------------------------------------
def test_01_real_constitution_loads_and_is_approved():
    meta = FoundryKernel().load_constitution(CONSTITUTION)
    assert meta["Document ID"] == "HVT-0001"
    assert meta["Status"] == "Approved"
    # Amended 20 Nov 2026 (DR-2026-11-20-06 / -12): Art. XIV.6 added by Art. XI amendment -> v1.3.
    # Was: assert meta["Version"] == "1.2"
    assert meta["Version"] == "1.3"


def test_02_draft_constitution_refuses_boot(tmp_path):
    k = FoundryKernel()
    with pytest.raises(ConstitutionError, match="not 'Approved'"):
        k.load_constitution(write_constitution(tmp_path, status="Draft"))
    assert k.constitution is None


def test_03_wrong_document_id_refused(tmp_path):
    with pytest.raises(ConstitutionError, match="HVT-0001"):
        FoundryKernel().load_constitution(write_constitution(tmp_path, doc_id="HVT-0002"))


def test_04_missing_constitution_file_refused(tmp_path):
    with pytest.raises(ConstitutionError, match="not found"):
        FoundryKernel().load_constitution(tmp_path / "nope.md")


# ---- Gate 2: Object graph ---------------------------------------------------
def test_05_graph_refused_before_constitution():
    k = FoundryKernel()
    with pytest.raises(BootOrderError):
        k.load_graph(GRAPH)
    assert k.graph is None


def test_06_real_graph_loads_after_constitution(booted):
    assert "BUT-0001" in booted.objects
    assert booted.objects["HVT-0001"]["status"] == "Approved"


def test_07_duplicate_ids_refused(tmp_path):
    k = FoundryKernel(); k.load_constitution(write_constitution(tmp_path))
    with pytest.raises(GraphError, match="Duplicate"):
        k.load_graph(write_graph(tmp_path, [mk("HVT-0001"), mk("HVT-0001")]))


def test_08_dangling_relationship_refused(tmp_path):
    k = FoundryKernel(); k.load_constitution(write_constitution(tmp_path))
    with pytest.raises(GraphError, match="dangling"):
        k.load_graph(write_graph(tmp_path, [mk("ENG-0003", "Engine", "Reusable Asset",
                                               [{"type": "depends_on", "target_id": "DOC-9999"}])]))


def test_09_bad_status_vocabulary_and_stored_reuse_count_refused(tmp_path):
    k = FoundryKernel(); k.load_constitution(write_constitution(tmp_path))
    with pytest.raises(GraphError, match="vocabulary"):
        k.load_graph(write_graph(tmp_path, [mk("HVT-0009", status="Finished")]))
    with pytest.raises(GraphError, match="derived"):
        k.load_graph(write_graph(tmp_path, [mk("ENG-0009", "Engine", "Prototype", reuse_count=3)]))


# ---- Gate 3: Agent registration ---------------------------------------------
def test_10_agent_registration_refused_before_graph(tmp_path):
    k = FoundryKernel(); k.load_constitution(write_constitution(tmp_path))
    with pytest.raises(BootOrderError):
        k.register_agent("AGT-0001")


def test_11_registered_agents_are_the_hvt0002_rows(booted):
    a = booted.register_agent("AGT-0002")
    assert a["name"] == "Chief Architect" and a["office"] == "Architecture Office"
    agents = [o["name"] for o in booted.objects.values() if o["class"] == "Agent"]
    assert sorted(agents) == ["CEO Agent", "Chief Architect"]


def test_12_non_agent_registration_refused(booted):
    with pytest.raises(AgentRegistrationError, match="not 'Agent'"):
        booted.register_agent("ENG-0003")
    assert "ENG-0003" not in booted.agents


def test_13_unknown_object_registration_refused(booted):
    with pytest.raises(AgentRegistrationError, match="not in the object graph"):
        booted.register_agent("AGT-9999")


# ---- Gate 4: Workflow authority ---------------------------------------------
def test_14_workflow_refused_before_any_agent_registered(booted):
    with pytest.raises(BootOrderError):
        booted.execute_workflow("AGT-0002", "run_engine_search")


def test_15_authorized_workflow_runs_but_is_never_authoritative(with_agents):
    r = with_agents.execute_workflow("AGT-0002", "run_engine_search", {"capability": "stock"})
    assert r.office == "Architecture Office"
    assert r.status == "pending_human_review"


def test_16_workflow_outside_office_authority_refused(with_agents):
    with pytest.raises(UnauthorizedActionError, match="not authorized"):
        with_agents.execute_workflow("AGT-0002", "approve_constitution_amendment")
    with pytest.raises(UnauthorizedActionError, match="not authorized"):
        with_agents.execute_workflow("AGT-0001", "run_engine_search")


def test_17_ceo_agent_can_approve_governance_document_only_as_pending_review(with_agents):
    r = with_agents.execute_workflow("AGT-0001", "approve_governance_document", {"doc": "HVT-0004"})
    assert r.office == "CEO Office" and r.status == "pending_human_review"


def test_18_unknown_action_refused(with_agents):
    with pytest.raises(UnauthorizedActionError, match="not an action"):
        with_agents.execute_workflow("AGT-0001", "register_engine")


def test_19_every_refusal_is_audited(booted):
    with pytest.raises(KernelRefusal):
        booted.register_agent("ENG-0003")
    last = booted.audit_log[-1]
    assert last.outcome == "refused" and last.gate == "agent_registration"
    assert [e.gate for e in booted.audit_log[:2]] == ["constitution", "graph"]


# ---- Graph content checks against the documents -----------------------------
def test_20_derived_reuse_count_matches_hvt0003(booted):
    assert booted.reuse_count("ENG-0003") == 4          # Mystic Veil, Sales Trainer, Law Firm, Estate Agent
    assert booted.reuse_count("ENG-0001") == 0


def test_21_but0001_pilot_path_end_to_end(booted):
    card = booted.objects["BUT-0001"]["card"]
    assert card["recommended_engines"] == ["ENG-0001", "ENG-0002", "ENG-0003"]
    assert booted.related("BUT-0001", "classifies_under") == ["MKT-0001"]
    assert booted.related("MKT-0001", "classifies_under") == ["SEC-0001"]
    assert booted.solvers_of("PRB-0004") == []              # stock: capability gap, no Engine
    stock = card["required_capabilities"][3]
    assert stock["overlay"]["search_result"] == "PARTIAL MATCH"
    wish = booted.objects["WSH-0001"]
    assert wish["linked_problems"] == ["PRB-0004"] and wish["customer_asset_flag"] is True


def test_22_held_and_rejected_engines_are_not_registered(booted):
    assert "ENG-0005" not in booted.objects   # HOLD — DR-2026-09-04-12
    assert "ENG-0006" not in booted.objects   # rejected — DR-2026-09-04-10


def test_23_parse_header_handles_flattened_pdf_form():
    m = parse_metadata_header("Document ID: HVT-0001 Title: HVT Foundry Constitution Version: "
                              "1.2 Status: Approved Owner: CEO Agent Reviewed By: Chief Architect Dependencies: None")
    assert m["Status"] == "Approved" and m["Version"] == "1.2"


# ---- Labelled authority extensions (used by HVT Foundry Studio) -------------
def _ext_kernel(**kw):
    k = FoundryKernel(**kw)
    k.load_constitution(CONSTITUTION); k.load_graph(GRAPH)
    k.register_agent("AGT-0001"); k.register_agent("AGT-0002")
    return k


def test_24_extension_adds_action_only_to_named_office():
    k = _ext_kernel(extra_authority={"Architecture Office": {"capture_customer_wish": "DOC-0005 step 5"}},
                    extra_authority_source="TEST map (Draft)")
    r = k.execute_workflow("AGT-0002", "capture_customer_wish")
    assert r.authorized_by.startswith("TEST map (Draft)") and r.status == "pending_human_review"
    with pytest.raises(UnauthorizedActionError):
        k.execute_workflow("AGT-0001", "capture_customer_wish")


def test_25_extension_cannot_invent_office_or_redefine_core_action():
    with pytest.raises(KernelRefusal, match="unknown Office"):
        FoundryKernel(extra_authority={"Sales Office": {"x": "y"}}, extra_authority_source="t")
    with pytest.raises(KernelRefusal, match="core actions"):
        FoundryKernel(extra_authority={"Architecture Office": {"approve_constitution_amendment": "no"}},
                      extra_authority_source="t")
    with pytest.raises(KernelRefusal, match="source"):
        FoundryKernel(extra_authority={"Architecture Office": {"x": "y"}})


def test_26_core_behaviour_unchanged_without_extension():
    k = _ext_kernel()
    with pytest.raises(UnauthorizedActionError, match="not an action"):
        k.execute_workflow("AGT-0002", "capture_customer_wish")
