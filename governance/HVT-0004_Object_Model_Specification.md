Document ID: HVT-0004  
Title: HVT Object Model (HOM) Specification  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: CEO Agent  
Dependencies: HVT-0001, HVT-0002, HVT-0003  


> **Kept for the record.** The current version is `HVT-0004_Object_Model_Specification_v0.3.md` (DR-2026-10-18-01).

> **Kept for the record.** The current version is `HVT-0004_Object_Model_Specification_v1.0.md` (DR-2026-11-20-07).
---

# HVT-0004 — HVT Object Model (HOM) Specification

Document Class: Governance Document — Core Architecture Effective Date: Pending Approval Review Cycle: Annual, or upon material breach

## 1. Purpose

HVT-0001 through HVT-0003 established what the Foundry values, who acts on it, and what gets accumulated. Each is a document — readable by a human, but not natively queryable by a machine. This document introduces the layer beneath all three: a single object model that every Document, Asset, Engine, Package, Plugin, Theme, Agent, Project, Customer, Workflow, Decision, and Policy conforms to, so that the Foundry’s AI agents can query relationships between things instead of reading files to reconstruct them.

This does not replace HVT-0001–0003, or any future Markdown document. Per HVT-0001, Article VI.3, documentation is part of the product, and prose remains the record a human reviews and signs off on (Art. IV, V). The Object Model is a structured, machine-readable representation extracted from and kept in sync with the prose record — a second layer, not a substitute. Every object below carries a source_document reference back to the Markdown it was extracted from. If the two ever disagree, the Markdown document is authoritative until reconciled, per Art. V’s rule that undocumented (here: unreconciled) state carries no institutional weight.

## 2. The Twelve Object Types

| Type | Definition |
|---|---|
| Document | Any governance, technical, or record artifact under a HVT-#### or equivalent ID — Constitution, Authority Model, Registry, scope docs, decision records. |
| Asset | The generic parent class for anything logged in HVT-0003 — the umbrella under which Engine, Package, Plugin, and Theme all sit. Used directly for asset categories without a dedicated subtype (Documentation, Prompt Library, Design System, Industry Template, Test Suite, Brand Asset). |
| Engine | Generalized business-process logic per HVT-0001 Art. III.1. A subtype of Asset. |
| Package | Versioned, dependency-isolated, installable unit built from an Engine, per Art. III.2. A subtype of Asset. |
| Plugin | Modular extension adding capability to an Engine or Package without modifying its core, per Art. XIII.3.d. A subtype of Asset. |
| Theme | Reusable visual/design language system, per Art. XIII.3.c. A subtype of Asset. |
| Agent | An AI or human actor registered to exactly one Office per HVT-0002 §4. |
| Project | A client engagement or named application — e.g., an application an Engine is used by. |
| Customer | The client entity a Project is delivered for, distinct from the Project itself; holds Customer Assets per Art. VIII. |
| Workflow | A defined sequence of steps an Office or Agent executes repeatedly — the candidate form a process takes before it matures into an Engine (Art. III.1). |
| Decision | A logged Decision Record per Art. V — the atomic unit of institutional memory. |
| Policy | A rule with standing force that is not itself a full Document — e.g., a single Article, an approved Exception, a standard. |

## 3. The Universal Object Schema

Every object, regardless of type, carries the following fields. Type-specific fields extend this base; none override it.

```yaml
Object:
  id:               # Unique, class-prefixed (HVT-####, ENG-####, PKG-####, etc.)
  class:            # One of the twelve types in §2
  name:             # Human-readable name
  owner:            # Accountable Office or Agent, per HVT-0002 §3
  status:           # Lifecycle stage — vocabulary depends on class (see §4)
  version:          # Current version
  relationships:    # List of {type, target_id} — see §5 for relationship vocabulary
  dependencies:     # Subset of relationships where type = depends_on
  approvals:        # List of {approver, date, decision_ref}
  change_history:   # List of {version, date, change, ref} — mirrors a Document's Changelog table
  authority:        # The Document or Article this object operates under (traceability per Art. V)
  reuse_count:      # Derived: count of used_by relationships — applies to Asset-class objects
  source_document:  # The Markdown Document ID this object was extracted from, if any
```

This schema reconciles two things that must stay consistent: the Asset-specific shorthand (id, class, owner, lifecycle, dependencies, approvals, versions, reuse_count) and the general twelve-type shorthand (Unique ID, Owner, Status, Relationships, Version, Change history, Authority, Dependencies). lifecycle and status are the same field; versions and version are the same field, with change_history carrying the version-by-version detail. One schema, two summaries.

## 4. Status Vocabularies by Class

Status is a controlled vocabulary, not free text, and it differs by class:

| Class | Status Vocabulary |
|---|---|
| Document | Draft → Approved → Superseded (HVT-0001 Appendix A) |
| Engine / Package / Theme / Plugin / Asset | Prototype → Engine → Package → Reusable Asset (HVT-0001 Art. III.4) |
| Agent | Registered → Active → Retired |
| Project | Proposed → Active → Delivered → Closed |
| Decision | Logged → Superseded (never deleted, per Art. V.3–V.4) |
| Policy | Proposed → Ratified → Exception-in-effect → Amended |

An object’s status may only move forward along its vocabulary, or be explicitly superseded — mirroring HVT-0001’s rule that history is never edited, only appended to.

## 5. Relationship Vocabulary

Relationships are directed edges between two object IDs. The recognized types:

| Relationship | Meaning | Example |
|---|---|---|
| governs | A Document or Policy sets binding rules for the target | HVT-0001 governs HVT-0002 |
| contains | A Document or Registry holds the target as an entry | HVT-0003 contains ENG-0003 |
| owns | An Office or Agent is accountable for the target | Architecture Office owns HVT-0003 |
| depends_on | The object requires the target to function or to be valid | ENG-0003 depends_on DOC-0001 |
| used_by | An Asset is consumed by a Project | ENG-0003 used_by Mystic Veil |
| produces | An Office or Agent originates the target | Design produces a Theme |
| belongs_to | An Agent is registered to an Office | Chief Architect belongs_to Architecture Office |
| approves | An Office or Agent signed off on the target | Chief Architect approves HVT-0003 |
| supersedes | The object replaces a prior version of another object | HVT-0002 v0.2 supersedes HVT-0002 v0.1 |
| escalates_to | Defines the escalation path from one Office to another | Deployment escalates_to Quality Assurance |

reuse_count (§3) is not stored directly — it is always derived by counting used_by edges pointing at a given Asset. This keeps the count from drifting out of sync with the actual relationship data, per Art. V’s traceability requirement.

## 6. Example Queries This Enables

Once objects and relationships exist in this form, questions that previously required reading every file become graph traversals:

- “Which reusable assets are used by more than three products?” → Filter objects where class is Engine/Package/Theme/Plugin and status = Reusable Asset, then count outgoing used_by edges, threshold > 3.
- “Which engines depend on deprecated documentation?” → Filter objects where class = Engine, traverse depends_on edges to Document objects, filter those Documents where status = Superseded.
- “What does this decision trace back to?” → From a Decision object, follow authority to the governing Article, and depends_on to any prior Decision it builds on.

None of these require an Agent to open and read a Markdown file end to end — they require the object graph to be current, per §1’s sync requirement.

## 7. Current Foundry Object Graph (Seed State)

The known objects and relationships as of this document’s drafting are instantiated as structured data in a companion file, not restated here as prose:

HVT_Foundry/graph/foundry_graph.json

That file is the first working instance of this schema, seeded from HVT-0001 through HVT-0003 and the ENG-0003 ledger entry. It carries forward the same open item flagged in HVT-0003 §2 — ENG-0003’s depends_on edges to DOC-0001 and DOC-0004 are present but marked unresolved, exactly as they stand in the prose registry. The graph does not silently resolve what the Markdown record left open.

## 8. Implementation Note — Not Yet Decided

This document specifies the model. It deliberately does not commit to a storage backend, since that is a build decision, not a governance one, and per this Foundry’s own preference for open-source tooling, several fit:

- File-based (current state): the schema expressed as JSON/YAML, versioned in the same repository as the Markdown documents. Zero infrastructure, fully diffable, human-reviewable per Art. IV — but querying at scale means loading the whole graph into memory each time.
- Embedded graph library (e.g., NetworkX, Python): same file-based storage, but queries like §6 are written once as functions instead of re-derived by hand each time. Still no server to run.
- Standalone graph database (e.g., Neo4j Community Edition):
- real query language (Cypher), scales past what fits comfortably in memory, but introduces infrastructure the Foundry would need to own and document per Art. VI (module replaceability — the database itself would need to stay swappable).

No object or relationship defined in this document depends on which of these is chosen. That decision can be made, and changed, later without touching this schema.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Initial draft. Establishes the twelve object types, universal schema, status vocabularies, relationship taxonomy, and seeds the first object graph from HVT-0001–0003. |
