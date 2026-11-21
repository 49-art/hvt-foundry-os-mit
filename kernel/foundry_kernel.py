"""
HVT-0005 — The Foundry Kernel
=============================

A small, dependency-free Python runtime (standard library only) that enforces
the HVT Foundry Constitution (HVT-0001) through four hard-gated boot steps:

    1. Load the Constitution   — refuses to boot if it isn't Approved.
    2. Load the Object Graph   — refuses if the Constitution hasn't loaded first.
    3. Register Agents         — refuses to register anything that isn't Agent-class.
    4. Execute a Workflow      — checks the acting Agent's Office against HVT-0002's
                                 authority model before allowing the action;
                                 refuses closed if unauthorized.

Design notes (each traceable to a governing clause):

* Gates are strictly ordered. Calling a later step before an earlier one has
  succeeded raises BootOrderError — the kernel never "skips ahead".
* Every refusal raises a subclass of KernelRefusal AND is written to the audit
  log (HVT-0001 Art. V: every decision documented; Art. XII: deviations logged).
* A permitted workflow never produces an authoritative result. Its output is
  marked "pending_human_review" (HVT-0001 Art. IV.3 and Art. X: authority is
  conferred only by human review; automation may not remove the review step).
* The authority table below is transcribed from HVT-0002 §4.2 — the only
  registered agents are "CEO Agent" and "Chief Architect". The table text is
  unchanged since v0.2. On 18 Oct 2026 the founder (Travis Lee Swift) approved
  HVT-0002 as v0.3 (DR-2026-10-18-01), so AUTHORITY_SOURCE now says so. No
  agent, office or power was added by that approval.
* The kernel reads files; it never writes to governance documents or the graph.

Status of this code: written 2026-09-25 to the specification in the project
README (see DR-2026-09-25-02). It is Prototype-grade and has not been reviewed
or approved by any Foundry office. The optional labelled authority extension
(used by HVT Foundry Studio) was added the same day — see DR-2026-09-25-07.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "FoundryKernel", "KernelRefusal", "BootOrderError", "ConstitutionError",
    "GraphError", "AgentRegistrationError", "UnauthorizedActionError",
    "WorkflowResult", "AUTHORITY", "parse_metadata_header",
]

KERNEL_ID = "HVT-0005"
KERNEL_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Refusals
# ---------------------------------------------------------------------------

class KernelRefusal(Exception):
    """Base class for every refusal the kernel issues. Refusals fail closed."""
    gate = "unknown"


class BootOrderError(KernelRefusal):
    """A boot step was attempted before the step it depends on succeeded."""
    gate = "boot_order"


class ConstitutionError(KernelRefusal):
    """Gate 1: the Constitution is missing, malformed, or not Approved."""
    gate = "constitution"


class GraphError(KernelRefusal):
    """Gate 2: the object graph is missing or violates the Object Model."""
    gate = "graph"


class AgentRegistrationError(KernelRefusal):
    """Gate 3: the object offered for registration is not a valid Agent."""
    gate = "agent_registration"


class UnauthorizedActionError(KernelRefusal):
    """Gate 4: the acting Agent's Office is not authorized for the action."""
    gate = "workflow_authority"


# ---------------------------------------------------------------------------
# HVT-0002 v0.2 §4.2 — Agent authority table (transcribed, not invented)
# ---------------------------------------------------------------------------

AUTHORITY_SOURCE = "HVT-0002 v1.0 §4.2 (Approved, 20 Nov 2026 — DR-2026-11-20-06; AI agent table text unchanged since v0.2)"

#: Office each registered agent belongs to (HVT-0002 §4.1: exactly one office).
AGENT_OFFICE: Dict[str, str] = {
    "CEO Agent": "CEO Office",
    "Chief Architect": "Architecture Office",
}

#: Actions each Office's registered agent is authorized to perform.
#: Keys are machine names; values carry the source wording from HVT-0002 §4.2.
AUTHORITY: Dict[str, Dict[str, str]] = {
    "CEO Office": {
        "approve_constitution_amendment": "Approve Constitution amendments",
        "resolve_final_escalation": "resolve final escalations",
        "approve_governance_document": "approve Governance Documents (HVT-####)",
    },
    "Architecture Office": {
        "run_engine_search": "Run Engine Search",
        "approve_asset_maturity_promotion": "approve asset maturity promotion",
        "maintain_asset_registry": "own HVT-0003",
    },
}

ALL_ACTIONS = {a for acts in AUTHORITY.values() for a in acts}

# ---------------------------------------------------------------------------
# HVT-0004 v0.1 — schema and vocabularies used by graph validation
# ---------------------------------------------------------------------------

#: Universal fields every object must carry (HVT-0004 §3). reuse_count is
#: derived (HVT-0004 §5) and therefore must NOT be stored.
REQUIRED_FIELDS = ("id", "class", "name", "owner", "status", "version",
                   "relationships", "authority")

#: Status vocabularies (HVT-0004 §4) plus proposed vocabularies from
#: HVT-0006 §9 / HVT-0007 §4 — canonical from HVT-0004 v1.0 (DR-2026-11-20-07).
STATUS_VOCAB: Dict[str, set] = {
    "Document": {"Draft", "Approved", "Superseded"},
    "Engine": {"Prototype", "Engine", "Package", "Reusable Asset"},
    "Package": {"Prototype", "Engine", "Package", "Reusable Asset"},
    "Theme": {"Prototype", "Engine", "Package", "Reusable Asset"},
    "Plugin": {"Prototype", "Engine", "Package", "Reusable Asset"},
    # HVT-0003 records Documentation assets as "Draft" — a known discrepancy
    # with HVT-0004 §4, carried as recorded rather than silently corrected.
    "Asset": {"Prototype", "Engine", "Package", "Reusable Asset", "Draft"},
    "Agent": {"Registered", "Active", "Retired"},
    "Project": {"Proposed", "Active", "Delivered", "Closed"},
    "Decision": {"Logged", "Superseded"},
    "Policy": {"Proposed", "Ratified", "Exception-in-effect", "Amended"},
    "Customer Session": {"Open", "Closed", "Actioned"},
    "Customer Wish": {"Logged", "Under Review", "Engine Search Required",
                      "Configured", "Accepted", "Rejected by Customer",
                      "Superseded"},
    # HVT-0004 v1.0 §9.3 (DR-2026-11-20-07): lifecycle words for classes that had none.
    "Sector": {"Registered", "Superseded"},
    "Market Industry": {"Registered", "Superseded"},
    "Business Model": {"Registered", "Superseded"},
    "Problem": {"Registered", "Superseded"},
    "Integration": {"Registered", "Superseded"},
    "Solution Component": {"Registered", "Superseded"},
    "Business Type": {"Registered", "Approved", "Superseded"},
}

#: Relationship vocabulary: HVT-0004 §5 plus proposed HVT-0006 §5 extensions,
#: and "implements" as used by DR-2026-08-04-08 (flagged in HVT-0004 v0.2 Draft).
RELATIONSHIPS = {
    "governs", "contains", "owns", "depends_on", "used_by", "produces",
    "belongs_to", "approves", "supersedes", "escalates_to",
    "works_with", "requires", "optional_with", "classifies_under", "solves",
    "integrates_via", "implements",
    "family_of",   # Problem → Problem overlap, HVT-0004 v1.0 §9.8 (DR-2026-11-20-07)
}

_ID_RE = re.compile(r"^[A-Z]{2,4}-\d{4}")


def parse_metadata_header(text: str) -> Dict[str, str]:
    """Parse the HVT-0001 Appendix A header block from a Markdown document.

    Accepts either one field per line ("Status: Approved") or the flattened
    single-paragraph form produced by PDF extraction.
    """
    keys = ["Document ID", "Title", "Version", "Status", "Owner",
            "Reviewed By", "Dependencies"]
    head = text.split("\n---", 1)[0] if "\n---" in text else text[:2000]
    head = head.replace("**", "")
    pattern = r"(" + "|".join(re.escape(k) for k in keys) + r"):"
    parts = re.split(pattern, head)
    meta: Dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        k, v = parts[i], parts[i + 1].strip()
        v = v.splitlines()[0].strip() if v else v
        if k not in meta:
            meta[k] = v
    return meta


@dataclass
class AuditEntry:
    timestamp: str
    gate: str
    outcome: str          # "ok" | "refused"
    detail: str


@dataclass
class WorkflowResult:
    agent: str
    office: str
    action: str
    authorized_by: str
    payload: Dict[str, Any]
    status: str = "pending_human_review"   # Art. IV.3 — never authoritative
    note: str = ("Output is not authoritative until a qualified human accepts, "
                 "rejects, or amends it (HVT-0001 Art. IV.2.c, IV.3).")


@dataclass
class FoundryKernel:
    """The four-gate Foundry runtime."""

    constitution: Optional[Dict[str, str]] = None
    graph: Optional[Dict[str, Any]] = None
    objects: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    agents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    audit_log: List[AuditEntry] = field(default_factory=list)
    #: Optional, clearly-labelled authority extensions supplied by an application
    #: built on the kernel (e.g. HVT Foundry Studio). They can only ADD actions to
    #: an Office that already exists in AUTHORITY, never to a new Office, and every
    #: result they authorize names ``extra_authority_source`` instead of HVT-0002.
    extra_authority: Dict[str, Dict[str, str]] = field(default_factory=dict)
    extra_authority_source: str = ""

    def __post_init__(self) -> None:
        unknown = set(self.extra_authority) - set(AUTHORITY)
        if unknown:
            raise KernelRefusal(f"Authority extension refused: unknown Office(s) {sorted(unknown)}.")
        clash = {a for acts in self.extra_authority.values() for a in acts} & ALL_ACTIONS
        if clash:
            raise KernelRefusal(f"Authority extension refused: cannot redefine core actions {sorted(clash)}.")
        if self.extra_authority and not self.extra_authority_source:
            raise KernelRefusal("Authority extension refused: a source/label is required.")

    # -- audit ---------------------------------------------------------------
    def _log(self, gate: str, outcome: str, detail: str) -> None:
        self.audit_log.append(AuditEntry(
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            gate, outcome, detail))

    def _refuse(self, exc_type: type, detail: str) -> None:
        self._log(exc_type.gate, "refused", detail)
        raise exc_type(detail)

    # -- gate 1 --------------------------------------------------------------
    def load_constitution(self, path: str | Path) -> Dict[str, str]:
        """Gate 1. Load HVT-0001 and refuse unless its Status is Approved."""
        p = Path(path)
        if not p.is_file():
            self._refuse(ConstitutionError, f"Constitution file not found: {p}")
        meta = parse_metadata_header(p.read_text(encoding="utf-8"))
        if meta.get("Document ID") != "HVT-0001":
            self._refuse(ConstitutionError,
                         f"Expected Document ID HVT-0001, found {meta.get('Document ID')!r} "
                         "(Appendix A header missing or wrong document).")
        status = meta.get("Status", "")
        if status != "Approved":
            self._refuse(ConstitutionError,
                         f"Constitution status is {status!r}, not 'Approved'. A Draft "
                         "document cannot be cited as authoritative (Appendix A.3). "
                         "Boot refused.")
        self.constitution = meta
        self._log("constitution", "ok",
                  f"HVT-0001 v{meta.get('Version')} loaded (status Approved).")
        return meta

    # -- gate 2 --------------------------------------------------------------
    def load_graph(self, path: str | Path) -> Dict[str, Any]:
        """Gate 2. Load the object graph; refuse unless the Constitution is loaded."""
        if self.constitution is None:
            self._refuse(BootOrderError,
                         "Object graph load refused: the Constitution has not been loaded.")
        p = Path(path)
        if not p.is_file():
            self._refuse(GraphError, f"Graph file not found: {p}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            self._refuse(GraphError, f"Graph is not valid JSON: {e}")
        self._validate_graph(data)
        self.graph = data
        self.objects = {o["id"]: o for o in data["objects"]}
        self._log("graph", "ok", f"{len(self.objects)} objects loaded from {p.name}.")
        return data

    def _validate_graph(self, data: Any) -> None:
        if not isinstance(data, dict) or not isinstance(data.get("objects"), list):
            self._refuse(GraphError, "Graph must be an object with an 'objects' list.")
        seen: Dict[str, Dict[str, Any]] = {}
        for o in data["objects"]:
            missing = [f for f in REQUIRED_FIELDS if f not in o]
            if missing:
                self._refuse(GraphError,
                             f"Object {o.get('id', '?')} missing universal fields {missing} (HVT-0004 §3).")
            if o["id"] in seen:
                self._refuse(GraphError, f"Duplicate object id {o['id']} (Appendix A.2: IDs never reused).")
            if "reuse_count" in o:
                self._refuse(GraphError,
                             f"Object {o['id']} stores reuse_count; it must be derived from used_by edges (HVT-0004 §5).")
            vocab = STATUS_VOCAB.get(o["class"])
            if vocab is not None and o["status"] not in vocab:
                self._refuse(GraphError,
                             f"Object {o['id']} ({o['class']}) has status {o['status']!r}, "
                             f"not in its vocabulary {sorted(vocab)} (HVT-0004 §4).")
            seen[o["id"]] = o
        for o in data["objects"]:
            for rel in o["relationships"]:
                if rel.get("type") not in RELATIONSHIPS:
                    self._refuse(GraphError,
                                 f"Object {o['id']} uses unknown relationship {rel.get('type')!r} (HVT-0004 §5).")
                tgt = str(rel.get("target_id", ""))
                if _ID_RE.match(tgt) and tgt not in seen:
                    self._refuse(GraphError,
                                 f"Object {o['id']} has a dangling {rel['type']} edge to {tgt}.")

    # -- gate 3 --------------------------------------------------------------
    def register_agent(self, object_id: str) -> Dict[str, Any]:
        """Gate 3. Register an Agent-class object from the graph; refuse anything else."""
        if self.graph is None:
            self._refuse(BootOrderError,
                         "Agent registration refused: the object graph has not been loaded.")
        obj = self.objects.get(object_id)
        if obj is None:
            self._refuse(AgentRegistrationError,
                         f"Refused: {object_id!r} is not in the object graph. An unregistered "
                         "agent has no standing to act (HVT-0002 §4.2).")
        if obj["class"] != "Agent":
            self._refuse(AgentRegistrationError,
                         f"Refused: {object_id} is class {obj['class']!r}, not 'Agent'. "
                         "Only Agent-class objects may be registered (HVT-0002 §4).")
        office = obj.get("office")
        offices = [r["target_id"] for r in obj["relationships"] if r["type"] == "belongs_to"]
        if not office or offices != [office]:
            self._refuse(AgentRegistrationError,
                         f"Refused: {object_id} must belong to exactly one Office (HVT-0002 §4.1).")
        if AGENT_OFFICE.get(obj["name"]) != office:
            self._refuse(AgentRegistrationError,
                         f"Refused: {obj['name']!r} is not in the HVT-0002 §4.2 registration table "
                         f"for {office!r}.")
        self.agents[object_id] = obj
        self._log("agent_registration", "ok", f"{object_id} ({obj['name']}) registered to {office}.")
        return obj

    # -- gate 4 --------------------------------------------------------------
    def execute_workflow(self, agent_id: str, action: str,
                         payload: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Gate 4. Run an action only if the agent's Office is authorized for it."""
        if not self.agents:
            self._refuse(BootOrderError,
                         "Workflow refused: no agents have been registered.")
        agent = self.agents.get(agent_id)
        if agent is None:
            self._refuse(UnauthorizedActionError,
                         f"Workflow refused: {agent_id!r} is not a registered agent.")
        extra_actions = {a for acts in self.extra_authority.values() for a in acts}
        if action not in ALL_ACTIONS and action not in extra_actions:
            self._refuse(UnauthorizedActionError,
                         f"Workflow refused: {action!r} is not an action defined in {AUTHORITY_SOURCE}.")
        office = agent["office"]
        allowed = AUTHORITY.get(office, {})
        extra = self.extra_authority.get(office, {})
        if action not in allowed and action not in extra:
            self._refuse(UnauthorizedActionError,
                         f"Workflow refused: {agent['name']} ({office}) is not authorized to "
                         f"{action!r}. Per {AUTHORITY_SOURCE} that belongs to another Office. "
                         "Failing closed.")
        if action in allowed:
            basis = f"{AUTHORITY_SOURCE}: “{allowed[action]}”"
        else:
            basis = f"{self.extra_authority_source}: “{extra[action]}”"
        result = WorkflowResult(agent=agent["name"], office=office, action=action,
                                authorized_by=basis, payload=dict(payload or {}))
        self._log("workflow_authority", "ok",
                  f"{agent['name']} performed {action}; output pending human review.")
        return result

    # -- graph queries (HVT-0004 §6) -------------------------------------------
    def reuse_count(self, asset_id: str) -> int:
        """Derived per HVT-0004 §5: count of used_by edges on the asset."""
        self._require_graph()
        o = self.objects[asset_id]
        return sum(1 for r in o["relationships"] if r["type"] == "used_by")

    def related(self, object_id: str, rel_type: str) -> List[str]:
        self._require_graph()
        return [r["target_id"] for r in self.objects[object_id]["relationships"]
                if r["type"] == rel_type]

    def solvers_of(self, problem_id: str) -> List[str]:
        """Which Engines have a `solves` edge to this Problem?"""
        self._require_graph()
        return sorted(o["id"] for o in self.objects.values()
                      if any(r["type"] == "solves" and r["target_id"] == problem_id
                             for r in o["relationships"]))

    def _require_graph(self) -> None:
        if self.graph is None:
            raise BootOrderError("Graph not loaded.")
