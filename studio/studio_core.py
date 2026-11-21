"""
HVT Foundry Studio — core logic (no web code here, so it can be tested directly).

Implements the DOC-0005 High-Street Tablet Design Loop on top of the Foundry
Kernel (kernel/foundry_kernel.py) and the object graph (graph/foundry_graph.json).

Rules this file follows (all from the record):
* Every action goes through the kernel's Gate 4 authority check first. If the
  kernel refuses, nothing is written except the refusal in the audit log.
* Every output is "pending_human_review" (HVT-0001 Art. IV).
* Nothing is ever deleted. A change writes a new revision that supersedes the
  previous one (DOC-0005 "No wish is ever deleted — only superseded").
* The Studio never writes to governance documents or to foundry_graph.json.
  Sessions and wishes it creates are local draft records in studio/data/.
* Only data from the documents is shown. Anything not verified is flagged.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kernel"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from foundry_kernel import (FoundryKernel, KernelRefusal, BootOrderError,  # noqa: E402
                            AgentRegistrationError, UnauthorizedActionError)
import factcheck  # noqa: E402
import live_search  # noqa: E402
import shop_app  # noqa: E402
import card_app  # noqa: E402
import cards  # noqa: E402
import connectors as hvt_connectors  # noqa: E402
import connectors.custom_api  # noqa: E402,F401
from netutil import fetch as net_fetch  # noqa: E402
from settings import Settings  # noqa: E402

CONSTITUTION = ROOT / "governance" / "HVT-0001_Constitution.md"
GRAPH = ROOT / "graph" / "foundry_graph.json"
DEFAULT_STATE = Path(__file__).resolve().parent / "data" / "studio_state.json"

STUDIO_VERSION = "0.3.0"
ACTING_AGENT = "AGT-0002"          # Chief Architect — Architecture Office (HVT-0002 §4.2)

#: Studio actions, added to the Architecture Office ONLY, through the kernel's
#: labelled extension mechanism. Approval status of each part: see STUDIO_AUTHORITY_SOURCE and DR-2026-10-18-01.
STUDIO_AUTHORITY_SOURCE = ("HVT Foundry Studio action map (DR-2026-09-25-07, DR-2026-09-26-08 and DR-2026-09-26-09 actions: "
                           "Approved — DR-2026-11-20-11, 20 Nov 2026; Chief Architect review done by the CEO Office under "
                           "Exception EXC-2026-11-20-01 (DR-2026-11-20-02); earlier founder approval DR-2026-10-18-01; "
                           "basis: DOC-0005 steps, DR-2026-08-04-09 precedent under HVT-0002 §3.2)")
STUDIO_AUTHORITY = {
    "Architecture Office": {
        "open_customer_session": "DOC-0005 step 1 — Open Session",
        "classify_business": "DOC-0005 step 2 — Classify / Re-classify",
        "run_configurator": "DOC-0005 step 3 — Run Configurator (ENG-0004 logic)",
        "record_owner_response": "DOC-0005 step 4 — Owner Reviews on Tablet",
        "capture_customer_wish": "DOC-0005 step 5 — Capture Wishes",
        "close_customer_session": "DOC-0005 step 6 — Close Session",
        "resolve_wish": "DOC-0005 step 7 — Return Path (re-configure / out of scope)",
        "offer_new_configuration": "DOC-0005 step 8 — New configuration offered back",
        # Added by DR-2026-09-26-08 (Approved 20 Nov 2026, DR-2026-11-20-11)
        "run_live_search": "Find for my business — live web/map search for the owner (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01)",
        "save_search_result": "Save a live search result to the shop's session (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01)",
        "build_shop_app": "Generate the shop's own app from the session (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01; Art. VIII customer asset)",
        "export_shop_app": "Export the shop's own app as a zip the shop owns (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01; Art. VIII)",
        "update_studio_settings": "Change Studio settings such as search keys (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01)",
        "manage_connector": "Add keys to, test or run an outside connector (DR-2026-09-26-08, Approved — DR-2026-11-20-11; Chief Architect review by the CEO Office, EXC-2026-11-20-01)",
        # Added by DR-2026-09-26-09 (Approved 20 Nov 2026, DR-2026-11-20-11)
        "preview_card_template": "Show a card app template's 4-star preview with (demo) content (DR-2026-09-26-09, Approved — DR-2026-11-20-11)",
        "build_card_app": "Generate a shop's own app from a card template and the shop's module choices (DR-2026-09-26-09, Approved — DR-2026-11-20-11; Art. VIII customer asset)",
        "export_card_app": "Export a card-built shop app as a zip the shop owns, without private data or keys (DR-2026-09-26-09, Approved — DR-2026-11-20-11; Art. VIII)",
    }
}

SIZES = ["1 Person", "2–5 Staff", "5–20 Staff", "20+"]                     # HVT-0006 §4
BUDGETS = ["£0–50", "£50–200", "£200–1000", "£1000+"]                       # HVT-0006 §4 (monthly)
BUDGET_CEILING = {"£0–50": 50, "£50–200": 200, "£200–1000": 1000, "£1000+": None}
TECH = ["None", "Basic", "Intermediate", "Advanced"]                        # HVT-0006 §4
PRIORITIES = ["Must", "Should", "Could"]                                   # HVT-0006 §9.2
#: Which Solution Component industries apply to each card (DR-2026-11-20-10); integrations on the card add more.
SLC_INDUSTRY_TAGS = {"BUT-0001": ["salon"], "BUT-0002": ["retail"], "BUT-0003": ["retail"], "BUT-0004": ["retail"],
                     "BUT-0005": ["retail"], "BUT-0006": ["healthcare"], "BUT-0007": []}

WISH_OUTCOMES = {"reconfigure": "Configured", "engine_search": "Engine Search Required",
                 "out_of_scope": "Under Review"}

# Reserved/used IDs in the record: SES-0001 (template), SES-0002 (dry run),
# SES-0003 (blank live session, blocked on DOC-0008). WSH-0001 (template).
FIRST_FREE = {"SES": 4, "WSH": 2}

ENGINE_PLAIN = {
    "ENG-0001": "Customer records, appointment book and basic loyalty",
    "ENG-0002": "Simple website, online booking and local map, editable from a phone",
    "ENG-0003": "Taking payments (card, online) through your chosen payment provider",
    "ENG-0004": "The Configurator — matches a business to engines and tools",
}
ENGINE_STATUS_PLAIN = {
    "Prototype": "designed and registered, not built yet",
    "Engine": "built, not yet packaged",
    "Package": "packaged",
    "Reusable Asset": "built and already used in 4 other projects",
}


class StudioRefusal(Exception):
    """A refusal from the kernel or a rule of the loop. Carries an HTTP-ish code."""
    def __init__(self, message: str, code: int = 403):
        super().__init__(message)
        self.code = code


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class Store:
    """Append-only JSON store. Records are lists of revisions; nothing is removed."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.lock = threading.RLock()
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data = {"studio_version": STUDIO_VERSION, "created": now_iso(),
                         "counters": {}, "records": {"sessions": [], "wishes": [],
                                                     "proposals": [], "responses": [],
                                                     "engine_searches": []},
                         "events": [], "audit": []}
            self.save()

    def save(self) -> None:
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=1, ensure_ascii=False)
            os.replace(tmp, self.path)

    def next_id(self, prefix: str) -> str:
        c = self.data["counters"]
        n = max(c.get(prefix, FIRST_FREE.get(prefix, 1) - 1) + 1, FIRST_FREE.get(prefix, 1))
        c[prefix] = n
        return f"{prefix}-{n:04d}"

    def append(self, kind: str, record: Dict[str, Any]) -> Dict[str, Any]:
        revs = [r for r in self.data["records"][kind] if r["id"] == record["id"]]
        record = deepcopy(record)
        record["rev"] = (max(r["rev"] for r in revs) + 1) if revs else 1
        record["supersedes"] = f"{record['id']} rev {record['rev'] - 1}" if revs else None
        record["recorded_at"] = now_iso()
        self.data["records"][kind].append(record)
        return record

    def current(self, kind: str) -> List[Dict[str, Any]]:
        latest: Dict[str, Dict[str, Any]] = {}
        for r in self.data["records"][kind]:
            if r["id"] not in latest or r["rev"] > latest[r["id"]]["rev"]:
                latest[r["id"]] = r
        return list(latest.values())

    def get(self, kind: str, rid: str) -> Optional[Dict[str, Any]]:
        revs = [r for r in self.data["records"][kind] if r["id"] == rid]
        return max(revs, key=lambda r: r["rev"]) if revs else None

    def history(self, kind: str, rid: str) -> List[Dict[str, Any]]:
        return sorted([r for r in self.data["records"][kind] if r["id"] == rid], key=lambda r: r["rev"])


class Studio:
    def __init__(self, state_path: Path | str | None = None,
                 constitution: Path = CONSTITUTION, graph: Path = GRAPH,
                 fetcher=None, settings_path: Path | str | None = None):
        self.constitution_path = Path(constitution)
        self.graph_path = Path(graph)
        self.store = Store(Path(state_path or os.environ.get("HVT_STUDIO_DATA", DEFAULT_STATE)))
        for kind in ("saved_results", "shop_apps", "searches", "card_apps"):
            self.store.data["records"].setdefault(kind, [])
        self.data_dir = self.store.path.parent
        self.fetcher = fetcher or net_fetch
        self.settings = Settings(settings_path or (self.data_dir / "settings.json"))
        self.cache = live_search.Cache(self.data_dir / "cache" / "search_cache.json")
        self.cred_store = hvt_connectors.CredentialStore(self.data_dir / "connectors")
        self.lock = threading.RLock()
        self.kernel: Optional[FoundryKernel] = None
        self.boot_steps: List[Dict[str, Any]] = []
        self._audit_mark = 0
        self.boot_id = None
        self.boot()

    # ------------------------------------------------------------------ boot
    def boot(self) -> Dict[str, Any]:
        """Run the kernel's four gates, including the refusal checks, and record each."""
        with self.lock:
            k = FoundryKernel(extra_authority=STUDIO_AUTHORITY,
                              extra_authority_source=STUDIO_AUTHORITY_SOURCE)
            self._audit_mark = 0
            self.boot_id = now_iso()
            steps: List[Dict[str, Any]] = []

            def step(gate, title, fn, expect_refusal=False):
                t0 = time.perf_counter()
                try:
                    detail = fn()
                    outcome = "pass"
                except KernelRefusal as e:
                    detail = str(e)
                    outcome = "refused"
                ms = round((time.perf_counter() - t0) * 1000, 1)
                ok = (outcome == "refused") if expect_refusal else (outcome == "pass")
                steps.append({"gate": gate, "title": title, "outcome": outcome,
                              "expected": "refused" if expect_refusal else "pass",
                              "as_expected": ok, "detail": detail, "ms": ms})
                return ok

            step("0", "Boot-order check: load the graph before the Constitution",
                 lambda: k.load_graph(self.graph_path) and "loaded", expect_refusal=True)
            ok1 = step("1", "Gate 1 — Load the Constitution (must be Approved)",
                       lambda: "{Document ID} v{Version} — status {Status}".format(**k.load_constitution(self.constitution_path)))
            ok2 = ok1 and step("2", "Gate 2 — Load the object graph",
                               lambda: f"{len(k.load_graph(self.graph_path)['objects'])} objects validated")
            ok3 = ok2 and step("3", "Gate 3 — Register Agents (HVT-0002 §4.2 rows only)",
                               lambda: ", ".join(f"{a} {k.register_agent(a)['name']}" for a in ("AGT-0001", "AGT-0002")))
            if ok3:
                step("3", "Gate 3 refusal check — try to register ENG-0003 (not an Agent)",
                     lambda: k.register_agent("ENG-0003") and "registered", expect_refusal=True)
                ok4 = step("4", "Gate 4 — Authorized action (Chief Architect: open_customer_session)",
                           lambda: "authorized — " + k.execute_workflow(ACTING_AGENT, "open_customer_session",
                                                                      {"boot_check": True}).status)
                step("4", "Gate 4 refusal check — Chief Architect tries approve_constitution_amendment",
                     lambda: k.execute_workflow(ACTING_AGENT, "approve_constitution_amendment") and "allowed",
                     expect_refusal=True)
            else:
                ok4 = False
            all_ok = all(s["as_expected"] for s in steps) and ok4
            self._last_kernel = k
            self.kernel = k if all_ok else None
            self.boot_steps = steps
            self._sync_audit(context="boot")
            self.store.save()
            return {"ok": all_ok, "steps": steps, "boot_id": self.boot_id}

    @property
    def booted(self) -> bool:
        return self.kernel is not None

    def _sync_audit(self, context: str = "") -> None:
        k = self._last_kernel if self.kernel is None else self.kernel
        if k is None:
            return
        for e in k.audit_log[self._audit_mark:]:
            self.store.data["audit"].append({"timestamp": e.timestamp, "gate": e.gate,
                                             "outcome": e.outcome, "detail": e.detail,
                                             "boot_id": self.boot_id, "context": context})
        self._audit_mark = len(k.audit_log)

    _last_kernel: Optional[FoundryKernel] = None

    # ------------------------------------------------------------- authority
    def _authorize(self, action: str, payload: Dict[str, Any], agent: str = ACTING_AGENT) -> Dict[str, Any]:
        if not self.booted:
            raise StudioRefusal("The kernel has not booted cleanly, so no action can run. Open the Boot screen.", 503)
        try:
            r = self.kernel.execute_workflow(agent, action, payload)
        except KernelRefusal as e:
            self._sync_audit(context=action)
            self._event(action, payload, None, refused=str(e))
            self.store.save()
            raise StudioRefusal(str(e), 403)
        self._sync_audit(context=action)
        return {"agent": r.agent, "office": r.office, "action": r.action,
                "authorized_by": r.authorized_by, "status": r.status, "note": r.note}

    def _event(self, action, payload, kernel_result, refused=None, subject=None):
        ev = {"n": len(self.store.data["events"]) + 1, "timestamp": now_iso(), "action": action,
              "subject": subject, "payload": payload,
              "outcome": "refused" if refused else "ok", "refusal": refused,
              "kernel": kernel_result,
              "review_status": None if refused else "pending_human_review"}
        self.store.data["events"].append(ev)
        return ev

    def _do(self, action, payload, mutate, subject=None):
        with self.lock:
            kr = self._authorize(action, payload)
            result = mutate()
            self._event(action, payload, kr, subject=subject or (result or {}).get("id"))
            self.store.save()
            return {"result": result, "kernel": kr, "review_status": "pending_human_review"}

    def authority_test(self, case: str) -> Dict[str, Any]:
        """Deliberately attempt an action that must be refused (for the Audit screen)."""
        cases = {
            "ceo_captures_wish": ("AGT-0001", "capture_customer_wish"),
            "architect_amends_constitution": (ACTING_AGENT, "approve_constitution_amendment"),
            "architect_approves_governance_doc": (ACTING_AGENT, "approve_governance_document"),
        }
        if case not in cases:
            raise StudioRefusal(f"Unknown test case {case!r}.", 400)
        agent, action = cases[case]
        with self.lock:
            try:
                self._authorize(action, {"authority_test": case}, agent=agent)
            except StudioRefusal as e:
                return {"case": case, "agent": agent, "action": action, "refused": True, "message": str(e)}
            return {"case": case, "agent": agent, "action": action, "refused": False,
                    "message": "UNEXPECTED: action was allowed"}

    # ------------------------------------------------------------ graph data
    def obj(self, oid: str) -> Optional[Dict[str, Any]]:
        if not self.booted:
            return None
        return self.kernel.objects.get(oid)

    def business_types(self) -> List[Dict[str, Any]]:
        self._need_boot()
        out = []
        for o in self.kernel.objects.values():
            if o["class"] != "Business Type":
                continue
            full = "card" in o
            out.append({
                "id": o["id"], "name": o["name"],
                "data_level": "full" if full else "card-summary",
                "card_status": o.get("card_status", "Registered instance (DR-2026-08-04-04)"),
                "sector": self._sector(o), "market_industry": self._industry(o),
                "doc_path": self._card_doc(o["id"]),
                "gaps": self._type_gaps(o),
            })
        return sorted(out, key=lambda x: x["id"])

    def _need_boot(self):
        if not self.booted:
            raise StudioRefusal("The kernel has not booted cleanly. Open the Boot screen.", 503)

    def _sector(self, o):
        mkt = self.kernel.related(o["id"], "classifies_under")
        sec = self.kernel.related(mkt[0], "classifies_under") if mkt else []
        if sec:
            return f"{self.kernel.objects[sec[0]]['name']} ({sec[0]})"
        return (o.get("sector_prose") or "—") + " (prose only — no SEC ID minted)"

    def _industry(self, o):
        mkt = self.kernel.related(o["id"], "classifies_under")
        if mkt:
            return f"{self.kernel.objects[mkt[0]]['name']} ({mkt[0]})"
        return (o.get("market_industry_prose") or "—") + " (prose only — no MKT ID minted)"

    def _card_doc(self, but_id):
        if but_id == "BUT-0001":
            return "governance/HVT-0006_Industry_and_Compatibility_Taxonomy.md"
        for p in sorted((ROOT / "governance").glob(f"{but_id}_*.md")):
            return str(p.relative_to(ROOT))
        return None

    def _type_gaps(self, o) -> List[str]:
        if o["id"] == "BUT-0001":
            g = ["Stock / inventory tracking — no Foundry engine (Engine Search: PARTIAL MATCH, DR-2026-09-04-10); use DOC-0006 paths",
                 "Review & reply management — no Foundry engine (PARTIAL MATCH); use DOC-0007 paths",
                 "Staff rota / timesheets — not yet modelled",
                 "Overlay HVT-0006-OVL-0001 v1.0 Approved (DR-2026-11-20-04); Square vs sheet is the owner's choice at the session"]
            return g
        card = o.get("card")
        if not card:
            g = ["Problems are card text only — PRB IDs not minted as graph objects",
                 "No required capabilities or Solution Components linked in the graph for this type",
                 "Sector / Market Industry are prose only (no SEC/MKT IDs)",
                 "Tier-3 tools named on the card are unverified candidates"]
            if "pending" in (o.get("card_status") or "").lower():
                g.insert(0, "Card is a Draft pending Raj + Stan Lee — not approved")
            if not o.get("recommended_engines_on_card"):
                g.append("No recommended engines on the card yet")
            return g
        g = []
        for c in card.get("required_capabilities", []) + card.get("optional_capabilities", []):
            if not c.get("covered_by"):
                g.append(f"{c['name']} — no Foundry engine; {c.get('path') or 'GAP'}")
        g += [f"Out of scope: {x}" for x in card.get("out_of_scope", [])]
        if card.get("tier3_candidates"):
            g.append("Tier-3 tools on the shelf are unverified candidates: " + ", ".join(card["tier3_candidates"]))
        g.append("Design: Brand Intake + Stan Lee veto before any public surface (deferred, not waived)")
        return g

    def card_markdown(self, but_id: str) -> Optional[str]:
        rel = self._card_doc(but_id)
        if not rel:
            return None
        text = (ROOT / rel).read_text(encoding="utf-8")
        if but_id == "BUT-0001":
            start = text.find("### 2.2 Schema-Layer Walk")
            end = text.find("## 3. New Object Types")
            text = text[start:end] if start >= 0 and end > start else text
        return text

    def overlay_markdown(self) -> str:
        return (ROOT / "governance" / "HVT-0006_BUT-0001_capability_overlay.md").read_text(encoding="utf-8")

    # --------------------------------------------------------- configurator
    def configurator(self, but_id: str, size: str | None, budget: str | None, tech: str | None) -> Dict[str, Any]:
        """ENG-0004 logic as described in HVT-0006 §7, using only graph + fact-check data."""
        self._need_boot()
        o = self.kernel.objects.get(but_id)
        if not o or o["class"] != "Business Type":
            return {"business_type": but_id, "known": False, "engines": [], "components": [],
                    "capabilities": [], "problems": [],
                    "flags": ["This business is not a BusinessType in the graph. Nothing can be matched; "
                              "the Architecture Office would need to classify it (Art. XIV)."],
                    "filters": self._filter_notes(size, budget, tech)}
        engines_ids = o.get("card", {}).get("recommended_engines") or o.get("recommended_engines_on_card") or []
        engines = [self._engine_view(e) for e in engines_ids if e in self.kernel.objects]
        res: Dict[str, Any] = {"business_type": but_id, "name": o["name"], "known": True,
                               "data_level": "full" if "card" in o else "card-summary",
                               "engines": engines, "filters": self._filter_notes(size, budget, tech),
                               "sizing": {"size": size, "budget": budget, "tech": tech}}
        if "card" in o:
            card = o["card"]
            res["problems"] = [{"id": p, "name": self.kernel.objects[p]["name"],
                                "solved_by": self.kernel.solvers_of(p)}
                               for p in sorted(x["id"] for x in self.kernel.objects.values()
                                               if x["class"] == "Problem" and but_id in x.get("business_types", []))]
            res["capabilities"] = [dict(c, required=True) for c in card["required_capabilities"]] + \
                                  [dict(c, required=False) for c in card["optional_capabilities"]]
            slcs = []
            for x in self.kernel.objects.values():
                if x["class"] != "Solution Component":
                    continue
                sup = [r["target_id"] for r in x["relationships"] if r["type"] == "supersedes"]
                tags = SLC_INDUSTRY_TAGS.get(but_id, [])
                if any(s in card.get("integrations", []) for s in sup) or \
                        any(i.lower().startswith(tg) for i in x.get("supported_industries", []) for tg in tags):
                    slcs.append(self._component_view(x, sup, budget))
            res["components"] = sorted(slcs, key=lambda c: c["id"])
            res["deployment_targets"] = card.get("deployment_targets")
            res["pricing_bands"] = card.get("pricing_bands")
            res["time_to_deploy"] = card.get("time_to_deploy")
            res["flags"] = ["ENG-0004 Configurator is a Prototype (built as foundry_os, DR-2026-11-20-11); this Studio applies the "
                            "traversal HVT-0006 §7 describes to graph data only. Output is a proposal, not a decision.",
                            "Engine statuses are shown as recorded: Prototype engines are designed, not built.",
                            "Stock and review gaps have no Foundry engine by decision (DR-2026-09-04-10, Approved)."]
        else:
            res["problems"] = [{"id": p, "name": None, "solved_by": []} for p in o.get("problem_ids_on_card", [])]
            res["capabilities"] = []
            res["components"] = []
            res["flags"] = ["Only a card summary exists in the graph for this type. Problem names, connectors "
                            "and sizing are in the card document (shown below), not yet structured data.",
                            f"Card status: {o.get('card_status')}.",
                            "No Solution Components are linked to this type in the graph, so none are recommended."]
        return res

    def _engine_view(self, eid):
        e = self.kernel.objects[eid]
        return {"id": eid, "name": e["name"], "status": e["status"],
                "status_plain": ENGINE_STATUS_PLAIN.get(e["status"], e["status"]),
                "plain": ENGINE_PLAIN.get(eid, e.get("purpose", "")),
                "reuse_count": self.kernel.reuse_count(eid)}

    def _component_view(self, x, sup, budget):
        fc = factcheck.as_dict(x["id"])
        fit = "unknown"
        ceiling = BUDGET_CEILING.get(budget) if budget else None
        if fc and fc["min_monthly_gbp"] is not None:
            if budget is None or ceiling is None:
                fit = "fits"
            else:
                fit = "fits" if fc["min_monthly_gbp"] <= ceiling else "over"
        return {"id": x["id"], "name": x["name"], "vendor": x.get("vendor"), "category": x.get("category"),
                "tier": x.get("tier"), "partner_status": x.get("partner_status"),
                "compatible_engines": x.get("compatible_engines", []), "supersedes": sup,
                "id_provenance": x.get("id_provenance"), "factcheck": fc, "budget_fit": fit,
                "record_countries": x.get("supported_countries")}

    @staticmethod
    def _filter_notes(size, budget, tech):
        return {
            "size": {"value": size, "applied": False,
                     "note": "Recorded on the session. No size limits are documented for these engines or tools, so size does not narrow the list yet."},
            "budget": {"value": budget, "applied": bool(budget),
                       "note": "Compared with each tool's lowest verified monthly price (25 Sept 2026 fact-check). Card/transaction fees are extra. Tools with no verified price are shown as 'price unverified', never hidden."},
            "tech": {"value": tech, "applied": False,
                     "note": "Recorded on the session. No technical-ability ratings exist in the documents, so this does not narrow the list yet."},
        }

    def plain_package(self, cfg: Dict[str, Any]) -> List[Dict[str, str]]:
        """Owner-facing, plain-language summary of a proposal."""
        lines: List[Dict[str, str]] = []
        if not cfg.get("known"):
            return [{"head": "We can't match your business yet",
                     "body": "Your business isn't one of the types the Foundry has written up. We've noted it and the team will look at it. Nothing will be built without asking you."}]
        for e in cfg["engines"]:
            lines.append({"head": e["plain"], "body": f"{e['name']} ({e['id']}) — {e['status_plain']}."})
        comps = cfg.get("components", [])
        by_cat: Dict[str, List[str]] = {}
        for c in comps:
            ov = c["factcheck"]["overall"] if c["factcheck"] else "unverified"
            tag = {"verified": "", "partly": " (some facts unverified)"}.get(ov, " (unverified)")
            by_cat.setdefault(c["category"], []).append(c["name"] + tag)
        for cat, names in by_cat.items():
            lines.append({"head": f"{cat}: you choose",
                          "body": "Options: " + ", ".join(names) + ". You pick; the Foundry does not choose for you (HVT-0007 §7)."})
        for cap in cfg.get("capabilities", []):
            if cap.get("covered_by") is None and cap.get("overlay"):
                if "Stock" in cap["name"]:
                    lines.append({"head": "Knowing when stock is low",
                                  "body": "No Foundry software for this. If you use Square, turn on its low-stock alerts; otherwise keep a simple sheet and get a message when something is low (DOC-0006 v1.0)."})
                elif "Review" in cap["name"]:
                    lines.append({"head": "Replying to reviews",
                                  "body": "No Foundry software for this. Reply yourself on Google and WhatsApp, in your own words; optionally one polite review request after a visit (DOC-0007 v1.0)."})
            elif cap.get("covered_by") is None:
                lines.append({"head": cap["name"], "body": "Not covered yet — noted as a future item."})
        lines.append({"head": "Your data stays yours",
                      "body": "Your customer list, stock list and content belong to you and can be taken away at any time (Constitution Article VIII)."})
        return lines

    # ----------------------------------------------------------- the loop
    def open_session(self, business_type_id: str, business_name: str = "", location: str = "",
                     run_by: str = "", notes: str = "") -> Dict[str, Any]:
        self._need_boot()
        if business_type_id not in self.kernel.objects or self.kernel.objects[business_type_id]["class"] != "Business Type":
            raise StudioRefusal(f"{business_type_id!r} is not a BusinessType in the graph.", 400)
        payload = {"business_type_id": business_type_id}

        def mutate():
            sid = self.store.next_id("SES")
            o = self.kernel.objects[business_type_id]
            rec = {"id": sid, "class": "Customer Session", "project_id_or_business_type_id": business_type_id,
                   "business_name": business_name.strip(), "date": datetime.now().date().isoformat(),
                   "location": location.strip() or None, "owner": "Architecture Office (via HVT Foundry Studio)",
                   "run_by": run_by.strip() or None, "status": "Open", "notes": notes.strip(),
                   "linked_wishes": [], "follow_up_of": None,
                   "classification": {"business_type_id": business_type_id, "business_type_name": o["name"],
                                      "sector": self._sector(o), "market_industry": self._industry(o),
                                      "source": "graph", "owner_corrections": []},
                   "sizing": {"size": None, "budget": None, "tech": None},
                   "local_record": True,
                   "record_note": "Local Studio draft record. Not registered in foundry_graph.json. Pending human review."}
            return self.store.append("sessions", rec)
        return self._do("open_customer_session", payload, mutate)

    def _open_session_or_refuse(self, sid):
        s = self.store.get("sessions", sid)
        if not s:
            raise StudioRefusal(f"No session {sid}.", 404)
        if s["status"] != "Open":
            raise StudioRefusal(f"{sid} is {s['status']}. Closed sessions are permanent records; open a follow-up session instead.", 409)
        return s

    def classify(self, sid: str, business_type_id: str | None = None, sector: str | None = None,
                 market_industry: str | None = None, owner_words: str = "") -> Dict[str, Any]:
        s = self._open_session_or_refuse(sid)
        if business_type_id and business_type_id != "UNLISTED" and (
                business_type_id not in self.kernel.objects or
                self.kernel.objects[business_type_id]["class"] != "Business Type"):
            raise StudioRefusal(f"{business_type_id!r} is not a BusinessType.", 400)
        payload = {"session": sid, "business_type_id": business_type_id, "sector": sector,
                   "market_industry": market_industry, "owner_words": owner_words}

        def mutate():
            rec = deepcopy(s)
            c = rec["classification"]
            prior = {k: c.get(k) for k in ("business_type_id", "sector", "market_industry")}
            if business_type_id == "UNLISTED":
                c.update({"business_type_id": None, "business_type_name": "Not listed (owner-stated)"})
                rec["project_id_or_business_type_id"] = None
            elif business_type_id:
                o = self.kernel.objects[business_type_id]
                c.update({"business_type_id": business_type_id, "business_type_name": o["name"],
                          "sector": self._sector(o), "market_industry": self._industry(o)})
                rec["project_id_or_business_type_id"] = business_type_id
            if sector:
                c["sector"] = sector.strip() + " (owner-stated)"
            if market_industry:
                c["market_industry"] = market_industry.strip() + " (owner-stated)"
            if business_type_id or sector or market_industry or owner_words:
                c["source"] = "owner-corrected"
                c["owner_corrections"].append({"at": now_iso(), "owner_words": owner_words.strip(),
                                               "from": prior,
                                               "rule": "The customer's stated reality overrides any prior classification (DOC-0005)."})
            return self.store.append("sessions", rec)
        return self._do("classify_business", payload, mutate)

    def run_configurator(self, sid: str, size: str | None = None, budget: str | None = None,
                         tech: str | None = None) -> Dict[str, Any]:
        s = self._open_session_or_refuse(sid)
        for v, allowed, label in ((size, SIZES, "size"), (budget, BUDGETS, "budget"), (tech, TECH, "technical ability")):
            if v and v not in allowed:
                raise StudioRefusal(f"{label} must be one of {allowed} (HVT-0006 §4).", 400)
        payload = {"session": sid, "size": size, "budget": budget, "tech": tech}

        def mutate():
            but = s["classification"]["business_type_id"] or "UNLISTED"
            cfg = self.configurator(but, size, budget, tech)
            n = len([p for p in self.store.current("proposals") if p["session_id"] == sid]) + 1
            prop = {"id": f"{sid}/P{n}", "session_id": sid, "configuration": cfg,
                    "plain": self.plain_package(cfg), "status": "Offered — pending owner response",
                    "review_status": "pending_human_review"}
            rec = deepcopy(s)
            rec["sizing"] = {"size": size, "budget": budget, "tech": tech}
            self.store.append("sessions", rec)
            return self.store.append("proposals", prop)
        return self._do("run_configurator", payload, mutate)

    def record_owner_response(self, sid: str, proposal_id: str, decision: str, owner_words: str = "") -> Dict[str, Any]:
        s = self._open_session_or_refuse(sid)
        if decision not in ("accept", "reject"):
            raise StudioRefusal("decision must be 'accept' or 'reject'.", 400)
        prop = self.store.get("proposals", proposal_id)
        if not prop or prop["session_id"] != sid:
            raise StudioRefusal(f"No proposal {proposal_id} in {sid}.", 404)
        payload = {"session": sid, "proposal": proposal_id, "decision": decision, "owner_words": owner_words}

        def mutate():
            p2 = deepcopy(prop)
            p2["status"] = ("Accepted by owner" if decision == "accept" else "Rejected by owner") + \
                           " — recorded; pending Foundry human review"
            self.store.append("proposals", p2)
            n = len(self.store.data["records"]["responses"]) + 1
            resp = self.store.append("responses", {
                "id": f"{sid}/R{n}", "session_id": sid, "proposal_id": proposal_id, "decision": decision,
                "owner_words": owner_words.strip(),
                "meaning": "The owner's own decision about their business. It is not a Foundry approval of anything."})
            # Step 8: if this is a follow-up session, carry the owner's answer onto re-configured wishes.
            if s.get("follow_up_of"):
                for w in self.store.current("wishes"):
                    if w["id"] in s.get("carried_wishes", []) and w["status"] == "Configured":
                        w2 = deepcopy(w)
                        w2["status"] = "Accepted" if decision == "accept" else "Rejected by Customer"
                        w2["resolution"] = (w.get("resolution") or "") + f" | Owner {decision}ed the new configuration in {sid}."
                        self.store.append("wishes", w2)
            return resp
        return self._do("record_owner_response", payload, mutate)

    def capture_wish(self, sid: str, description: str, priority: str | None = None,
                     linked_problems: List[str] | None = None, linked_capabilities: str = "",
                     customer_asset_flag: bool = False) -> Dict[str, Any]:
        s = self._open_session_or_refuse(sid)
        if not description or not description.strip():
            raise StudioRefusal("A wish needs the owner's own words.", 400)
        if priority and priority not in PRIORITIES:
            raise StudioRefusal(f"priority must be one of {PRIORITIES} or left blank.", 400)
        payload = {"session": sid, "description": description, "priority": priority}

        def mutate():
            wid = self.store.next_id("WSH")
            w = self.store.append("wishes", {
                "id": wid, "class": "Customer Wish", "session_id": sid,
                "description": description.strip(), "description_is_owner_words": True,
                "priority": priority or None, "status": "Logged",
                "linked_problems": linked_problems or [], "linked_capabilities": linked_capabilities.strip() or None,
                "resolution": None, "resolution_type": None,
                "customer_asset_flag": bool(customer_asset_flag), "local_record": True})
            rec = deepcopy(s)
            rec["linked_wishes"] = rec["linked_wishes"] + [wid]
            self.store.append("sessions", rec)
            return w
        return self._do("capture_customer_wish", payload, mutate)

    def close_session(self, sid: str) -> Dict[str, Any]:
        s = self._open_session_or_refuse(sid)
        payload = {"session": sid}

        def mutate():
            rec = deepcopy(s)
            rec["status"] = "Closed"
            rec["closed_at"] = now_iso()
            return self.store.append("sessions", rec)
        return self._do("close_customer_session", payload, mutate)

    def review_queue(self) -> List[Dict[str, Any]]:
        sessions = {s["id"]: s for s in self.store.current("sessions")}
        q = []
        for w in self.store.current("wishes"):
            if w["resolution_type"] is None:
                s = sessions.get(w["session_id"], {})
                q.append(dict(w, session_status=s.get("status"),
                              business_type=s.get("classification", {}).get("business_type_name"),
                              business_name=s.get("business_name")))
        return sorted(q, key=lambda w: w["id"])

    def resolve_wish(self, wid: str, outcome: str, reason: str, capability: str = "") -> Dict[str, Any]:
        w = self.store.get("wishes", wid)
        if not w:
            raise StudioRefusal(f"No wish {wid}.", 404)
        if outcome not in WISH_OUTCOMES:
            raise StudioRefusal(f"outcome must be one of {sorted(WISH_OUTCOMES)}.", 400)
        if w["resolution_type"] is not None:
            raise StudioRefusal(f"{wid} is already resolved ({w['resolution_type']}). History is kept; it cannot be re-resolved here.", 409)
        s = self.store.get("sessions", w["session_id"])
        if s and s["status"] == "Open":
            raise StudioRefusal(f"Close {s['id']} first — the return path starts after leaving the tablet (DOC-0005 step 7).", 409)
        if not reason or not reason.strip():
            raise StudioRefusal("A reason is required — every resolution is logged (DOC-0005 step 7).", 400)
        action = "run_engine_search" if outcome == "engine_search" else "resolve_wish"
        payload = {"wish": wid, "outcome": outcome, "reason": reason, "capability": capability}

        def mutate():
            w2 = deepcopy(w)
            w2["status"] = WISH_OUTCOMES[outcome]
            w2["resolution_type"] = outcome
            label = {"reconfigure": "Re-configuration using existing engines",
                     "engine_search": "Formal Engine Search logged (Art. II)",
                     "out_of_scope": "Out of scope for now (still logged)"}[outcome]
            w2["resolution"] = f"{label}: {reason.strip()}"
            if outcome == "out_of_scope":
                w2["status_note"] = ("HVT-0006 §9.2 has no 'out of scope' status; status left at 'Under Review' "
                                     "with the outcome in resolution — flagged in OPEN_ITEMS.")
            if outcome == "engine_search":
                n = len(self.store.data["records"]["engine_searches"]) + 1
                es = self.store.append("engine_searches", {
                    "id": f"{wid}/ES{n}", "wish_id": wid, "capability": capability.strip() or w.get("linked_capabilities"),
                    "questions": ["a. Does an existing engine already solve this, in whole or in part?",
                                  "b. Can an existing engine be extended, parameterized or composed?",
                                  "c. Only if (a) and (b) are 'no', with evidence, may new functionality be authorized."],
                    "result": None, "status": "Logged — to be performed and recorded by the Architecture Office",
                    "note": "Logging a search does not authorize any new Engine (DR-2026-08-04-06 binding rule)."})
                w2["engine_search_id"] = es["id"]
            w3 = self.store.append("wishes", w2)
            self._maybe_action_session(w["session_id"])
            return w3
        return self._do(action, payload, mutate)

    def _maybe_action_session(self, sid):
        s = self.store.get("sessions", sid)
        if not s or s["status"] != "Closed":
            return
        wishes = [self.store.get("wishes", w) for w in s["linked_wishes"]]
        if wishes and all(w["resolution_type"] for w in wishes):
            rec = deepcopy(s)
            rec["status"] = "Actioned"
            self.store.append("sessions", rec)

    def offer_follow_up(self, sid: str) -> Dict[str, Any]:
        s = self.store.get("sessions", sid)
        if not s:
            raise StudioRefusal(f"No session {sid}.", 404)
        if s["status"] == "Open":
            raise StudioRefusal("Close the session before offering a new configuration.", 409)
        carried = [w for w in s["linked_wishes"] if self.store.get("wishes", w)["resolution_type"] == "reconfigure"]
        payload = {"from_session": sid, "carried_wishes": carried}

        def mutate():
            nid = self.store.next_id("SES")
            rec = deepcopy(s)
            rec.update({"id": nid, "status": "Open", "linked_wishes": [], "follow_up_of": sid,
                        "carried_wishes": carried, "date": datetime.now().date().isoformat(),
                        "notes": f"Follow-up of {sid}: new configuration offered back (DOC-0005 step 8)."})
            rec.pop("closed_at", None)
            rec["classification"] = deepcopy(s["classification"])
            rec["classification"]["owner_corrections"] = list(s["classification"]["owner_corrections"])
            new = self.store.append("sessions", rec)
            return new
        return self._do("offer_new_configuration", payload, mutate)

    # --------------------------------------------------------------- views
    def session_detail(self, sid: str) -> Dict[str, Any]:
        s = self.store.get("sessions", sid)
        if not s:
            raise StudioRefusal(f"No session {sid}.", 404)
        return {"session": s, "history": self.store.history("sessions", sid),
                "saved_results": self.saved_results(sid),
                "shop_app": self._shop_app_record(sid),
                "proposals": [p for p in self.store.current("proposals") if p["session_id"] == sid],
                "responses": [r for r in self.store.current("responses") if r["session_id"] == sid],
                "wishes": [self.store.get("wishes", w) for w in s["linked_wishes"]],
                "carried_wishes": [self.store.get("wishes", w) for w in s.get("carried_wishes", [])],
                "problems": self._problems_for(s["classification"]["business_type_id"])}

    def _problems_for(self, but_id):
        if not but_id or not self.booted:
            return []
        o = self.kernel.objects.get(but_id, {})
        if "card" in o:
            return [{"id": x["id"], "name": x["name"]} for x in self.kernel.objects.values()
                    if x["class"] == "Problem" and but_id in x.get("business_types", [])]
        return [{"id": p, "name": None} for p in o.get("problem_ids_on_card", [])]

    def sessions(self) -> List[Dict[str, Any]]:
        return sorted(self.store.current("sessions"), key=lambda s: s["id"], reverse=True)

    def wish_history(self, wid: str) -> List[Dict[str, Any]]:
        return self.store.history("wishes", wid)

    def audit(self) -> Dict[str, Any]:
        return {"kernel_audit": list(reversed(self.store.data["audit"])),
                "studio_events": list(reversed(self.store.data["events"]))}

    def summary(self) -> Dict[str, Any]:
        cur = self.store.current("sessions")
        return {"studio_version": STUDIO_VERSION, "booted": self.booted, "boot_id": self.boot_id,
                "boot_steps": self.boot_steps, "acting_agent": "AGT-0002 Chief Architect (Architecture Office)",
                "counts": {"sessions_open": sum(1 for s in cur if s["status"] == "Open"),
                           "sessions_total": len(cur),
                           "wishes_total": len(self.store.current("wishes")),
                           "queue": len(self.review_queue()),
                           "events": len(self.store.data["events"]),
                           "saved_results": len(self.store.current("saved_results")),
                           "shop_apps": len(self.store.current("shop_apps"))},
                "vocab": {"sizes": SIZES, "budgets": BUDGETS, "tech": TECH, "priorities": PRIORITIES},
                "banners": ["Prototype. Every output is pending human review (HVT-0001 Art. IV).",
                            "DOC-0008 is not yet approved, so SES-0003 (the first live build session) is still blocked. "
                            "Sessions made here are local draft records until reviewed.",
                            "Owner 'accept' records the owner's own choice. It is not a Foundry approval."],
                "state_file": str(self.store.path),
                "search_ready": {"brave": bool(self.settings.load().get("brave_api_key")),
                                 "serpapi": bool(self.settings.load().get("serpapi_key"))}}


    # =================================================================== v0.2
    # Live search, saved results, shop apps, connectors, settings (DR-2026-09-26-08)
    def _authorized_event(self, action, payload, subject=None):
        with self.lock:
            kr = self._authorize(action, payload)
            self._event(action, payload, kr, subject=subject)
            self.store.save()
            return kr

    def live_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cat = params.get("category") or "suppliers"
        if cat not in live_search.communities.CATEGORIES:
            raise StudioRefusal(f"category must be one of {list(live_search.communities.CATEGORIES)}.", 400)
        sid = params.get("session_id") or None
        if sid and not self.store.get("sessions", sid):
            raise StudioRefusal(f"No session {sid}.", 404)
        payload = {k: params.get(k) for k in ("category", "community", "postcode", "radius_m", "free_text", "session_id")}
        kr = self._authorized_event("run_live_search", payload, subject=sid)
        try:
            res = live_search.run_search(params, self.settings.load(), self.cache, self.fetcher)
        except ValueError as e:
            raise StudioRefusal(str(e), 400)
        with self.lock:
            n = len(self.store.data["records"]["searches"]) + 1
            self.store.append("searches", {"id": f"SRCH-{n:04d}", "session_id": sid, "params": payload,
                                           "web_count": len(res["web"]), "map_count": len(res["map"]),
                                           "errors": res["errors"], "started_at": res["started_at"]})
            self.store.save()
        res["kernel"] = kr
        res["review_status"] = "pending_human_review"
        return res

    SAVE_FIELDS = ("title", "url", "snippet", "source", "provider", "query", "query_lang", "query_lang_name", "checked_at",
                   "address", "distance_text", "kind", "phone", "website", "opening_hours", "category", "community")

    def save_search_result(self, sid: str, result: Dict[str, Any], note: str = "") -> Dict[str, Any]:
        if not self.store.get("sessions", sid):
            raise StudioRefusal(f"No session {sid}.", 404)
        if not isinstance(result, dict) or not result.get("url") or not result.get("title"):
            raise StudioRefusal("A result needs at least a title and a URL.", 400)
        if not str(result["url"]).startswith(("http://", "https://")):
            raise StudioRefusal("Result URL must be a web address.", 400)
        if not result.get("checked_at"):
            raise StudioRefusal("A result needs the date it was checked.", 400)
        clean = {k: (str(result[k])[:600] if result.get(k) is not None else None) for k in self.SAVE_FIELDS}
        payload = {"session": sid, "url": clean["url"], "title": clean["title"]}

        def mutate():
            dup = [r for r in self.store.current("saved_results") if r["session_id"] == sid and r["url"] == clean["url"]]
            if dup:
                return dup[0]
            n = len(self.store.current("saved_results")) + 1
            return self.store.append("saved_results", dict(clean, id=f"FND-{n:04d}", session_id=sid, saved_at=now_iso(),
                                                           note=note.strip()[:400], status="Saved",
                                                           label=live_search.LABEL, verified=False))
        return self._do("save_search_result", payload, mutate)

    def saved_results(self, sid: str) -> List[Dict[str, Any]]:
        return sorted([r for r in self.store.current("saved_results") if r["session_id"] == sid], key=lambda r: r["id"])

    # --------------------------------------------------------------- shop apps
    def _shop_app_record(self, sid):
        return self.store.get("shop_apps", f"APP-{sid}")

    def shop_app_draft(self, sid: str) -> Dict[str, Any]:
        s = self.store.get("sessions", sid)
        if not s:
            raise StudioRefusal(f"No session {sid}.", 404)
        rec = self._shop_app_record(sid)
        if rec:
            d = dict(rec["shop"])
        else:
            last = [x for x in self.store.data["records"]["searches"] if x.get("session_id") == sid and x["params"].get("postcode")]
            d = {"name": s.get("business_name") or "", "languages": ["en"], "products": [], "hours": [],
                 "postcode": last[-1]["params"]["postcode"].upper() if last else "", "announcement_on": True}
        d["suppliers_count"] = len(self.saved_results(sid))
        return {"session_id": sid, "shop": d, "record": {k: v for k, v in (rec or {}).items() if k not in ("password_hash",)} or None,
                "palettes": live_search.communities.palettes(), "languages": shop_app.shopbuild.LANG_NAMES}

    def build_shop_app(self, sid: str, shop: Dict[str, Any], password: str = "") -> Dict[str, Any]:
        s = self.store.get("sessions", sid)
        if not s:
            raise StudioRefusal(f"No session {sid}.", 404)
        rec = self._shop_app_record(sid)
        if not password and not (rec and rec.get("password_hash")):
            raise StudioRefusal("Ask the owner to choose a password for their admin page (6+ characters).", 400)
        shop = dict(shop or {})
        shop["suppliers"] = [{k: r.get(k) for k in ("title", "url", "snippet", "source", "address", "phone", "query",
                                                     "query_lang", "checked_at", "saved_at", "label")} for r in self.saved_results(sid)]
        shop["demo"] = bool(shop.get("demo"))
        if shop.get("postcode") and not shop.get("lat"):
            try:
                loc = live_search.lookup_postcode(shop["postcode"], self.fetcher, self.cache)
                shop["lat"], shop["lon"] = loc["lat"], loc["lon"]
            except live_search.NetError:
                pass                                          # map link falls back to a search by address
        try:
            cleaned = shop_app.shopbuild.clean_shop(dict(shop, admin={"password_hash": "x"}))
        except ValueError as e:
            raise StudioRefusal(str(e), 400)
        folder = (rec or {}).get("folder") or f"{shop_app.shopbuild.slugify(cleaned['name'])}-{sid.lower()}"
        payload = {"session": sid, "shop_name": cleaned["name"], "languages": cleaned["languages"], "folder": folder}

        def mutate():
            try:
                summary = shop_app.generate(shop, self.data_dir / "shops" / folder, password=password or None,
                                            existing_hash=(rec or {}).get("password_hash", ""))
            except ValueError as e:
                raise StudioRefusal(str(e), 400)
            h = shop_app.shopbuild.load_shop(self.data_dir / "shops" / folder)["admin"]["password_hash"]
            return self.store.append("shop_apps", {"id": f"APP-{sid}", "session_id": sid, "folder": folder, "shop": summary,
                                                   "password_hash": h, "preview_url": f"/shops/{folder}/",
                                                   "customer_asset": True,
                                                   "ownership": f"Belongs to {summary['name']} (Constitution Art. VIII)."})
        r = self._do("build_shop_app", payload, mutate)
        r["result"] = {k: v for k, v in r["result"].items() if k != "password_hash"}
        return r

    def export_shop_app(self, sid: str) -> Dict[str, Any]:
        rec = self._shop_app_record(sid)
        if not rec:
            raise StudioRefusal("Build the shop's app first.", 409)
        payload = {"session": sid, "folder": rec["folder"]}

        def mutate():
            name = rec["folder"] + "-app.zip"
            info = shop_app.export_zip(self.data_dir / "shops" / rec["folder"], self.data_dir / "exports" / name)
            return dict(info, download_url=f"/api/exports/{name}", id=rec["id"])
        return self._do("export_shop_app", payload, mutate)

    def shop_site_dir(self, folder: str) -> Optional[Path]:
        p = (self.data_dir / "shops" / folder / "site").resolve()
        return p if p.is_dir() and (self.data_dir / "shops").resolve() in p.parents else None

    def export_file(self, name: str) -> Optional[Path]:
        p = (self.data_dir / "exports" / name).resolve()
        return p if p.is_file() and (self.data_dir / "exports").resolve() in p.parents and p.suffix == ".zip" else None

    # --------------------------------------------------------------- card apps (v0.3)
    def card_list(self) -> List[Dict[str, Any]]:
        return cards.list_cards()

    def card_detail(self, card_id: str) -> Dict[str, Any]:
        try:
            c = cards.load_card(card_id)
        except cards.CardError as e:
            raise StudioRefusal(str(e), 404)
        return {"card": {k: v for k, v in c.items() if k != "modules"}, "modules": cards.catalogue(c),
                "statuses": list(cards.MODULE_STATUSES), "languages": shop_app.shopbuild.LANG_NAMES,
                "review_status": "pending_human_review"}

    def card_preview(self, card_id: str, preset_id: str, choices: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        try:
            c = cards.load_card(card_id)
            cards.preset(c, preset_id)
            on = cards.resolve(c, choices or {})
        except cards.CardError as e:
            raise StudioRefusal(str(e), 400)
        folder = f"preview-{card_id.lower()}-{preset_id}"
        payload = {"card": card_id, "preset": preset_id, "modules_on": sorted(k for k, v in on.items() if v)}

        def mutate():
            card_app.demo_preview(card_id, preset_id, self.data_dir / "card_apps" / folder, choices or {})
            return {"id": folder, "preview_url": f"/cardapps/{folder}/", "demo": True,
                    "note": "Preview with invented (demo) content. Booking, queue and stamp checks work in the running shop app."}
        return self._do("preview_card_template", payload, mutate)

    def build_card_app(self, card_id: str, shop: Dict[str, Any], password: str = "", app_id: str = "",
                       session_id: str = "") -> Dict[str, Any]:
        try:
            card = cards.load_card(card_id)
        except cards.CardError as e:
            raise StudioRefusal(str(e), 404)
        if session_id and not self.store.get("sessions", session_id):
            raise StudioRefusal(f"No session {session_id}.", 404)
        rec = self.store.get("card_apps", app_id) if app_id else None
        if app_id and not rec:
            raise StudioRefusal(f"No card app {app_id}.", 404)
        if not password and not (rec and rec.get("password_hash")):
            raise StudioRefusal("Ask the owner to choose a password for their admin page (6+ characters).", 400)
        shop = dict(shop or {})
        shop["demo"] = bool(shop.get("demo"))
        if shop.get("postcode") and not shop.get("lat"):
            try:
                loc = live_search.lookup_postcode(shop["postcode"], self.fetcher, self.cache)
                shop["lat"], shop["lon"] = loc["lat"], loc["lon"]
            except live_search.NetError:
                pass
        try:
            cleaned = card_app.cardbuild.clean_shop(card, dict(shop, admin={"password_hash": "x"}))
        except (ValueError, cards.CardError) as e:
            raise StudioRefusal(str(e), 400)
        rid = app_id or f"CAPP-{len(self.store.current('card_apps')) + 1:04d}"
        folder = (rec or {}).get("folder") or f"{card_app.cardbuild.slugify(cleaned['name'])}-{rid.lower()}"
        payload = {"card": card_id, "shop_name": cleaned["name"], "preset": cleaned["preset"], "folder": folder,
                   "modules_on": sorted(k for k, v in cleaned["modules"].items() if v), "session": session_id or None}

        def mutate():
            try:
                summary = card_app.generate(card_id, shop, self.data_dir / "card_apps" / folder, password=password or None,
                                            existing_hash=(rec or {}).get("password_hash", ""))
            except (ValueError, cards.CardError) as e:
                raise StudioRefusal(str(e), 400)
            h = card_app.cardbuild.load_shop(self.data_dir / "card_apps" / folder)["admin"]["password_hash"]
            return self.store.append("card_apps", {"id": rid, "card_id": card_id, "session_id": session_id or None,
                                                   "folder": folder, "shop_name": summary["name"], "preset": summary["preset"],
                                                   "modules": summary["modules"], "password_hash": h,
                                                   "preview_url": f"/cardapps/{folder}/", "customer_asset": True,
                                                   "ownership": f"Belongs to {summary['name']} (Constitution Art. VIII)."})
        r = self._do("build_card_app", payload, mutate)
        r["result"] = {k: v for k, v in r["result"].items() if k != "password_hash"}
        return r

    def card_apps(self) -> List[Dict[str, Any]]:
        return [{k: v for k, v in r.items() if k != "password_hash"} for r in sorted(self.store.current("card_apps"), key=lambda r: r["id"])]

    def export_card_app(self, app_id: str) -> Dict[str, Any]:
        rec = self.store.get("card_apps", app_id)
        if not rec:
            raise StudioRefusal("Build the shop's app first.", 409)
        payload = {"card_app": app_id, "folder": rec["folder"]}

        def mutate():
            name = rec["folder"] + "-app.zip"
            info = card_app.export_zip(self.data_dir / "card_apps" / rec["folder"], self.data_dir / "exports" / name)
            return dict(info, download_url=f"/api/exports/{name}", id=app_id)
        return self._do("export_card_app", payload, mutate)

    def card_app_dir(self, folder: str) -> Optional[Path]:
        base = (self.data_dir / "card_apps").resolve()
        p = (base / folder).resolve()
        return p if p.is_dir() and base in p.parents and (p / "data" / "card.json").exists() else None

    # --------------------------------------------------------------- settings
    def get_settings(self) -> Dict[str, Any]:
        return self.settings.public()

    def save_settings(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        changes = dict(changes or {})
        pw = changes.pop("studio_password", None)
        if pw:
            changes["studio_password_hash"] = shop_app.shopbuild.hash_password(pw)
        if changes.pop("clear_studio_password", False):
            changes["studio_password_hash"] = ""
        if "provider_order" in changes:
            order = [p for p in changes["provider_order"] if p in live_search.PROVIDERS]
            changes["provider_order"] = order or ["brave", "serpapi", "duckduckgo"]
        if "max_web_queries" in changes:
            changes["max_web_queries"] = max(1, min(int(changes["max_web_queries"]), 12))
        payload = {"changed": sorted(changes)}   # names only, never the key values
        return self._do("update_studio_settings", payload, lambda: self.settings.save(changes))

    def check_studio_password(self, pw: str) -> bool:
        h = self.settings.load().get("studio_password_hash")
        return bool(h) and shop_app.shopbuild.verify_password(pw, h)

    # ------------------------------------------------------------- connectors
    def _cm(self):
        return hvt_connectors.ConnectorManager(self.cred_store, self.fetcher, self.settings.load().get("contact_email", ""))

    def _scope(self, scope):
        scope = scope or "studio"
        if scope != "studio" and not self.store.get("sessions", scope):
            raise StudioRefusal(f"Scope must be 'studio' or a session ID, not {scope!r}.", 400)
        return scope

    def connectors_list(self, scope: str = "studio") -> Dict[str, Any]:
        scope = self._scope(scope)
        items = self._cm().list(scope)
        counts: Dict[str, int] = {}
        for c in items:
            counts[c["status"]] = counts.get(c["status"], 0) + 1
        return {"scope": scope, "items": items, "counts": counts, "statuses": list(hvt_connectors.STATUSES)}

    def connector_op(self, scope: str, cid: str, op: str, body: Dict[str, Any]) -> Dict[str, Any]:
        scope = self._scope(scope)
        if op not in ("credentials", "test", "run", "enable", "custom", "openapi"):
            raise StudioRefusal("Unknown connector operation.", 404)
        payload = {"scope": scope, "connector": cid, "op": op, "action": body.get("action") if op == "run" else None}

        def mutate():
            try:
                cm = self._cm()
                if op == "credentials":
                    return {"saved": self.cred_store.save_creds(scope, cid, body.get("values") or {})}
                if op == "test":
                    return cm.test(scope, cid)
                if op == "run":
                    return cm.run(scope, cid, body.get("action", ""), body.get("params") or {})
                if op == "enable":
                    return {"enabled": self.cred_store.set_enabled(scope, cid, bool(body.get("on")))}
                if op == "custom":
                    d = hvt_connectors.custom_api.validate_definition(body.get("definition") or {})
                    self.cred_store.save_custom_def(scope, body.get("slug", ""), d)
                    return {"id": "custom:" + body.get("slug", ""), "definition": d}
                if op == "openapi":
                    return hvt_connectors.custom_api.parse_openapi(body.get("spec"))
            except hvt_connectors.ConnectorError as e:
                raise StudioRefusal(str(e), e.code)
            except live_search.NetError as e:
                return {"ok": False, "message": str(e), "kind": e.kind}
        return self._do("manage_connector", payload, mutate)

    def community_catalogue(self) -> Dict[str, Any]:
        c = live_search.communities
        return {"categories": c.CATEGORIES,
                "communities": [{"id": x["id"], "label": x["label"], "lang_note": x.get("lang_note", ""),
                                 "languages": [{"code": l["code"], "name": l["name"], "dir": l["dir"],
                                                "checked_by_native_speaker": l["checked_by_native_speaker"], "note": l["note"]}
                                               for l in x["langs"]]} for x in c.COMMUNITIES]}

    def preview_queries(self, community: str, category: str, area: str = "London", free_text: str = "") -> List[Dict[str, Any]]:
        try:
            return live_search.communities.build_queries(community, category, area, True, free_text)
        except ValueError as e:
            raise StudioRefusal(str(e), 400)
