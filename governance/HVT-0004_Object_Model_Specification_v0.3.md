Document ID: HVT-0004  
Title: HVT Object Model (HOM) Specification  
Version: 0.3  
Previous version: 0.2   
Status: Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet  
Previous status (v0.2): Draft  
Approval record: DR-2026-10-18-01  
Owner: Architecture Office  
Reviewed By: pending — CEO Agent / Chief Architect (not reviewed)  
Dependencies: HVT-0001, HVT-0002, HVT-0003, HVT-0006, HVT-0006-OVL-0001, HVT-0007, DR-2026-08-04-03/-04/-05/-06/-07, DR-2026-09-04-12  
Supersedes (only if approved): HVT-0004 v0.1 — v0.1 remains the current version until then  
Drafted by: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25 — see DR-2026-09-25-06  


> **Read this first (added 18 Oct 2026).** Everything below this box is the earlier proposal, word for word, including its old "Draft" wording. Since 18 Oct 2026 this text is the current version, approved by the founder as interim (DR-2026-10-18-01). The older file is kept beside it.

> **Kept for the record.** The current version is `HVT-0004_Object_Model_Specification_v1.0.md` (DR-2026-11-20-07).
---

# HVT-0004 — HVT Object Model (HOM) Specification — v0.2 DRAFT

> **Draft notice.** This is a proposed consolidation, not an approved amendment. It gathers into one place the object types, vocabularies and relationships that HVT-0006 (§3, §4, §5, §9) and HVT-0007 (§2, §3, §4) proposed "pending formal HVT-0004 adoption" — the single consolidated bump named in DR-2026-08-04-07 (job B in the working list). Until a qualified reviewer approves it (HVT-0001 Art. IV, V), **HVT-0004 v0.1 stays in force** and nothing here is canonical. Text carried from v0.1 is unchanged; additions are marked **[v0.2]** and cite their source.

Document Class: Governance Document — Core Architecture Effective Date: Pending Approval Review Cycle: Annual, or upon material breach

## 1. Purpose

HVT-0001 through HVT-0003 established what the Foundry values, who acts on it, and what gets accumulated. Each is a document — readable by a human, but not natively queryable by a machine. This document introduces the layer beneath all three: a single object model that every Document, Asset, Engine, Package, Plugin, Theme, Agent, Project, Customer, Workflow, Decision, and Policy conforms to, so that the Foundry’s AI agents can query relationships between things instead of reading files to reconstruct them.

This does not replace HVT-0001–0003, or any future Markdown document. Per HVT-0001, Article VI.3, documentation is part of the product, and prose remains the record a human reviews and signs off on (Art. IV, V). The Object Model is a structured, machine-readable representation extracted from and kept in sync with the prose record — a second layer, not a substitute. Every object below carries a source_document reference back to the Markdown it was extracted from. If the two ever disagree, the Markdown document is authoritative until reconciled, per Art. V’s rule that undocumented (here: unreconciled) state carries no institutional weight.

## 2. The Twelve Object Types (v0.1, unchanged) and Proposed Additions [v0.2]

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


### 2.1 Proposed additional object types [v0.2]

Each row is copied from the document that proposed it. No definition has been reworded; no new type is invented here.

| Type | Definition (from source) | ID Prefix | Source |
|---|---|---|---|
| Sector | The broadest market grouping (e.g., Services, Retail, Hospitality). Parent of Market Industry. | SEC-#### | HVT-0006 §3 |
| Market Industry | A recognized vertical within a Sector (e.g., Personal Care). Parent of Business Type. Named “Market Industry” rather than “Industry” to avoid collision with HVT-0003’s existing “Industry Template” asset class, which retains IND-####. | MKT-#### | HVT-0006 §3; DR-2026-08-04-04 |
| Business Type | A specific kind of business within an Industry (e.g., Hair Salon). | BUT-#### | HVT-0006 §3 |
| Business Model | A structural variant of a Business Type (e.g., solo operator vs. multi-location chain) affecting which Workflows and Packages apply. | BUM-#### | HVT-0006 §3 |
| Problem | A recurring, named pain point surfaced by a Workflow, matched to one or more Solutions. | PRB-#### | HVT-0006 §3 |
| Integration | An external system or service a Product connects to (e.g., Stripe, Google Calendar). Distinct from Engine — an Integration is consumed, not built by the Foundry. | INT-#### | HVT-0006 §3 (see §2.3 below — relationship to Solution Component held open) |
| Product | The customer-facing, purchasable configuration of a Package — what the owner actually sees and buys. | PRD-#### | HVT-0006 §3 |
| Customer Wish | A captured piece of customer feedback or a stated want, tied to a live session, that the current registered Engines and Solution Components may not yet fully satisfy. | WSH-#### | HVT-0006 §9; DR-2026-08-04-06/-07 |
| Customer Session | A live interaction (e.g., a tablet session in-store) during which one or more Customer Wishes are captured. | SES-#### | HVT-0006 §9; DR-2026-08-04-06/-07 |
| Solution Component | The canonical schema for anything in Tier 1 or Tier 3: an interchangeable, vendor-tracked, licensable thing the Foundry recommends to fulfill a Required Capability. | SLC-#### | HVT-0007 §3.1; DR-2026-08-04-05 |

If adopted, the model would have **22 object types** (12 + 10). HVT-0006 §3 already notes Workflow, Engine, Package, Asset, Document and Decision are reused without change.

### 2.2 ID prefixes in use [v0.2]

v0.1 §3 names HVT-, ENG- and PKG- only. Prefixes actually used across the record: HVT-, ENG-, PKG-, DOC-, IND- (Industry Template, HVT-0003), DR- (Decision), WKF- (Workflow, WKF-0001), plus the ten in §2.1. **No prefix is defined for Agent, Project, Customer, Plugin, Theme or Policy.** The kernel's seed graph uses `AGT-` for the two HVT-0002 Agent rows as a working label only — flagged for decision, not adopted by this draft.

### 2.3 Integration vs. Solution Component — held open [v0.2]

HVT-0007 §3.1 says Solution Component "generalizes and supersedes" Integration, but the exact relationship was held open by the person's explicit “hold off” (HVT-0007 §9). This draft therefore lists **both** types and keeps the seven INT- records unchanged with `supersedes` edges from their SLC- records. Choosing "subtype" or "replacement" is a reviewer decision; either choice changes only wording, not data (HVT-0007 §3.1).

## 3. The Universal Object Schema

Every object, regardless of type, carries the following fields. Type-specific fields extend this base; none override it.

```yaml
Object:
  id:               # Unique, class-prefixed (HVT-####, ENG-####, PKG-####, etc.)
  class:            # One of the twelve types in §2 (or, if v0.2 is adopted, the additions in §2.1)
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


### 4.1 Proposed additional vocabularies [v0.2]

| Class / Field | Vocabulary | Source |
|---|---|---|
| Customer Session (status) | Open → Closed → Actioned | HVT-0006 §9.1 |
| Customer Wish (status) | Logged → Under Review → Engine Search Required → Configured → Accepted → Rejected by Customer → Superseded | HVT-0006 §9.2 |
| Solution Component (`partner_status` field) | Open Source → Public Integration → Verified → Certified → Strategic Partner → Enterprise Partner | HVT-0007 §4 |

Notes carried from the record, not resolved here:

- **Partner Status is a relationship ladder, not a fact-check result.** A vendor record being checked against the vendor's public pages (e.g. DR-2026-09-25-04) does not move `partner_status`; only a real change in the business relationship does (HVT-0007 §4).
- **"Official" → "Verified"** mapping from the working list is recorded as pending confirmation, not adopted.
- **No lifecycle vocabulary has been proposed** for Sector, Market Industry, Business Type, Business Model, Problem, Integration, Product or Solution Component. BusinessType cards use prose statuses (e.g. "queued", "pending Raj + Stan Lee"). This draft does not invent one; the seed graph uses the word "Registered" descriptively. Flagged for the reviewer.
- **Overlay status prose** such as "Configured-by-connector" is **not** a vocabulary value (DR-2026-09-04-10a); WSH-0001 stays at "Configured" with its explanation in prose.

### 4.2 Cross-cutting attributes (not object types, not statuses) [v0.2]

| Attribute | Values (controlled vocabulary) | Applies To | Source |
|---|---|---|---|
| Tier | 1 Open Source · 2 Foundry Assets · 3 Partner Products · 4 Customer Assets | Solution Component (Tiers 1, 3); Asset classes (Tier 2); Customer Assets (Tier 4) | HVT-0007 §2 |
| Deployment | Web · Tablet · Phone · PWA | Product | HVT-0006 §4 |
| Pricing Tier | Basic · Professional · Enterprise | Product | HVT-0006 §4 |
| Business Size | 1 Person · 2–5 Staff · 5–20 Staff · 20+ | Business Type instance | HVT-0006 §4 |
| Budget | £0–50 · £50–200 · £200–1000 · £1000+ | Business Type instance (monthly) | HVT-0006 §4 |
| Technical Ability | None · Basic · Intermediate · Advanced | Business Type instance | HVT-0006 §4 |

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


### 5.1 Proposed additional relationships [v0.2]

| Relationship | Meaning | Example | Source |
|---|---|---|---|
| works_with | Two Engines (or Products) are compatible and commonly deployed together, neither requiring the other. | Commerce Engine works_with Booking Engine | HVT-0006 §5 |
| requires | An Engine cannot function without another Engine present. | Commerce Engine requires Customer Engine | HVT-0006 §5 |
| optional_with | An Engine can be enhanced by another Engine, which is not required. | Commerce Engine optional_with Crypto Engine | HVT-0006 §5 |
| classifies_under | A lower taxonomy-spine object sits under a higher one. | Hair Salon classifies_under Personal Care | HVT-0006 §5 |
| solves | A Solution (Engine) addresses a named Problem. | Commerce Engine solves Slow checkout | HVT-0006 §5 |
| integrates_via | A Product connects to an external system through an Integration object. | Commerce Product integrates_via Stripe | HVT-0006 §5 |

**Candidate, not proposed by any source:** `implements` appears in DR-2026-08-04-08 but was never put forward as a vocabulary entry. It is listed here only so the reviewer can accept or reject it; the seed graph does not use it.

`supersedes` (already in v0.1) is the edge used from each SLC- record to the INT- record it replaces (HVT-0007 §3.1).

### 5.2 Read views (not new types) [v0.2]

The **BusinessType canonical card** (HVT-0006 §2.3) is a denormalized read view over the graph (sector rollup via `classifies_under`, problems via `solves`, and so on). It is not a separate object type and must never become a second source of truth — the same reasoning DR-2026-09-04-10a applied when it moved search outcomes into overlay HVT-0006-OVL-0001.

### 5.3 Explicitly not adopted or held [v0.2]

| Item | Why it is not in this draft | Source |
|---|---|---|
| StockItem (STI-####) and its edges | Proposed with ENG-0005; DR-2026-09-04-12 lists "StockItem adopted into HVT-0004" as explicitly not in the stamp, and ENG-0005 is on HOLD. | DR-2026-09-04-11 §3; DR-2026-09-04-12 |
| Final Integration vs. Solution Component relationship | Held open by explicit “hold off”. | HVT-0007 §3.1, §9 |
| Referral income / commercial agreement record | Deferred; not an architectural concept yet. | HVT-0007 §9 |
| Business Model placement on the BusinessType card | Undecided. | HVT-0006 §8 item 7 |
| complexity_score method | No scoring method defined. | HVT-0006 §8 item 6 |
| Agent ID prefix | Not defined in any source (see §2.2). | — |

## 6. Example Queries This Enables

Once objects and relationships exist in this form, questions that previously required reading every file become graph traversals:

- “Which reusable assets are used by more than three products?” → Filter objects where class is Engine/Package/Theme/Plugin and status = Reusable Asset, then count outgoing used_by edges, threshold > 3.
- “Which engines depend on deprecated documentation?” → Filter objects where class = Engine, traverse depends_on edges to Document objects, filter those Documents where status = Superseded.
- “What does this decision trace back to?” → From a Decision object, follow authority to the governing Article, and depends_on to any prior Decision it builds on.

None of these require an Agent to open and read a Markdown file end to end — they require the object graph to be current, per §1’s sync requirement.

## 7. Current Foundry Object Graph (Seed State)

**[v0.2]** As of 2026-09-25 the file exists (graph/foundry_graph.json, 72 objects) and is loaded and validated by the Foundry Kernel (kernel/foundry_kernel.py). It uses the §2.1 types ahead of adoption, as HVT-0006 §8 already allowed. ENG-0003's DOC-0001/DOC-0004 edges are now resolved per DR-2026-08-04-01. The original v0.1 text follows unchanged.

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
| 0.2 (Draft) | 2026-09-25 | Proposed consolidation of the extensions pending from HVT-0006 §3/§4/§5/§9 and HVT-0007 §2/§3/§4: ten added types, prefix list, session/wish/partner vocabularies, cross-cutting attributes, six added relationships, card-as-read-view rule, and an explicit held/not-adopted list. Drafted by AI executor on instruction from Travis Lee Swift (DR-2026-09-25-06). **Not reviewed, not approved.** v0.1 remains in force. |
| 0.3 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet. v0.2  text approved by the founder as interim (its header asks for CEO Agent and Chief Architect review; the Chief Architect role is vacant). Text unchanged from v0.2. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
