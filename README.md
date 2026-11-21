HVT Foundry HVT Foundry builds reusable AI-native business assets instead of one-off software. Every engagement is designed to leave the Foundry stronger than it found it: new capability is captured as a reusable Engine, not buried inside a single client’s codebase.  

---

The Foundry is governed by a written Constitution and a small, runnable Python kernel that enforces it — this repo is both the governance record and the code.

## Model-First, Not Software-First

“The Foundry does not begin an engagement by asking ‘What software should I build?’ It begins by asking: ‘What business is this, how does it operate, what problems does it face, and which combination of reusable Foundry assets solves those problems?’”

    - — HVT-0001, Article XIV

Software is the output of that question, never its starting point. The mechanism that answers it is the Business Ontology: a structured model of the relationships between businesses, their problems, the engines that solve them, the vendors and open-source tools that fulfill them, and how the whole thing gets priced and deployed.

## Repository Structure

```
governance/    The Constitution and six supporting governance documents (HVT-0001–0007)
decisions/     Decision Records — every architectural change, with rationale, made traceable
assets/        Registered Documentation assets (guides, procedures)
kernel/        The Foundry Kernel — a small Python runtime that enforces the Constitution
graph/         The live object graph: every registered Engine, Problem, Solution Component,
               Business Type instance, and Decision, as one JSON file
```

## Governance Documents

| ID | Title | Version | Status |
|---|---|---|---|
| HVT-0001 | Constitution | 1.3 | Approved (Art. XIV.6 added, DR-2026-11-20-06) |
| HVT-0002 | Organisation & Authority Model | 1.0 | Approved (DR-2026-11-20-06) |
| HVT-0003 | Business Asset Registry | 1.0 | Approved (DR-2026-11-20-02) |
| HVT-0004 | Object Model Specification | 1.0 | Approved (DR-2026-11-20-07) |
| HVT-0006 | Industry & Compatibility Taxonomy | 1.0 | Approved (DR-2026-11-20-08) |
| HVT-0006-OVL-0001…0007 | Capability overlays, BUT-0001…0007 | 1.0 | Approved (DR-2026-11-20-04 / -10) |
| HVT-0007 | Marketplace Layer & Solution Catalog | 1.0 | Approved (DR-2026-11-20-09) |
| BUT-0002…0007 | BusinessType cards | 1.0 | Approved — classification only (DR-2026-11-20-10) |
| DOC-0008 / SES-0002 / SES-0003 | Progressive Build Session, ladder script, live form | 1.0 | Approved (DR-2026-11-20-03) |
| DOC-0010 | QA Release Gate & Privacy Checklist | 1.0 | Approved (DR-2026-11-20-02) |

Note: HVT-0005 (the Foundry Kernel itself) is the code in kernel/, not a separate Markdown document.

Completed 20 Nov 2026 by DR-2026-11-20-01…12 on Tony Adams's instruction ("can you complete all decisions waiting and complete it"). The full version table, tests and live-human items are in DR-2026-11-20-12. Older versions are kept as their own files.

Every governance document follows the same lifecycle: Draft → Approved → Superseded. A Draft document cannot be cited as authoritative. Nothing is ever deleted — only superseded, with the prior version retained and linked.

## Decision Records

Every architectural change — a new object type, a resolved ambiguity, a Constitutional amendment — is logged in decisions/ as a numbered Decision Record (DR-YYYY-MM-DD-NN), stating what changed, why, what was deliberately left open, and what it supersedes. This is the project’s audit trail: Article V of the Constitution requires that every decision be documented, and that ambiguity be flagged rather than silently resolved.

## The Foundry OS (ENG-0004 Configurator — Prototype)

`foundry_os/` runs the DOC-0008 eight-rung ladder (classify → problems → shelf → match → quote → gaps → brand → deploy) from the graph only, and verifies the governance repository.

```
python3 -m foundry_os status        # boot + verify summary
python3 -m foundry_os verify        # headers, status words, ID reuse, Draft DRs carried, graph boot, DR numbering
python3 -m foundry_os cards         # the seven Business Type cards
python3 -m foundry_os decisions     # every decision record and its status
python3 -m foundry_os ladder foundry_os/examples/mina_theatre_SES-0002-F-0001.json
```

Every ladder output is marked "Draft — pending human review" and is never authoritative. It does not register ENG-0005; it only reports `eng_0005_trigger` for a live owner.

## The Foundry Kernel

The kernel (kernel/foundry_kernel.py) is a small, dependency-free Python runtime — standard library only — that enforces four hard-gated boot steps before any workflow can run:

1. Load the Constitution — refuses to boot if it isn’t Approved.
2. Load the Object Graph — refuses if the Constitution hasn’t loaded first.
3. Register Agents — refuses to register anything that isn’t Agent-class.
4. Execute a Workflow — checks the acting Agent’s Office against HVT-0002’s authority model before allowing the action; refuses closed if unauthorized.

## Run it

```
pip install -r requirements.txt
cd kernel
python3 demo_boot.py     # runs the full boot sequence, including both refusal paths
python3 -m pytest test_kernel.py -v   # 17 tests
```

demo_boot.py deliberately demonstrates two refusals, not just the happy path: an Agent attempting a workflow outside its Office’s authority, and an attempt to register a non-Agent object. A kernel that only shows success paths hasn’t actually demonstrated it enforces anything.

## The Object Graph

graph/foundry_graph.json is the live instance of the Object Model — every Engine, Problem, Solution Component, Business Type, Decision, and relationship the Foundry has registered, in one file. It currently holds real pilot data for a Hair Salon business type (BUT-0001), tracing the full path from classification through to a flagged capability gap and a logged customer wish — end to end, not just schema.

## Status

This is an active governance and architecture project, not a finished product. Several items are deliberately left open and tracked in the documents themselves rather than hidden: - Two Foundry Engines (Stock management, Review/reply management) are identified as capability gaps with no registered Engine yet — flagged for a formal Engine Search (Article II), not silently built. - Several Solution Component integration records are marked unverified pending confirmation against current vendor documentation. - HVT-0004’s canonical object-type list has several proposed extensions (from HVT-0006 and HVT-0007) awaiting formal adoption in a future version.

See the individual documents’ own “Scope” and “Open Items” sections for the full, current list.

## License

MIT — see LICENSE. Contributions and forks welcome.
