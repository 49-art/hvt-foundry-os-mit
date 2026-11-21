Document ID: HVT-0006  
Title: Industry & Compatibility Taxonomy  
Version: 1.0  
Previous version: 0.6  
Status: Approved  
Previous status (v0.6): Approved by Founder (Travis Lee Swift), 18 Oct 2026  
Approval record: DR-2026-11-20-08 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001 Art. XIV, HVT-0002, HVT-0003, HVT-0004  

---

# HVT-0006 — Industry & Compatibility Taxonomy

Document Class: Governance Document — Core Architecture (extension) Effective Date: Pending Approval Review Cycle: Annual, or upon material breach

## 1. Purpose

HVT-0004 established the Object Model — the twelve object types and relationship vocabulary every Foundry object conforms to. This document extends that model with a specific taxonomy: the chain from market classification down to a priced, deployable configuration, so that a high-street business owner’s answer to “what kind of business am I” can be mechanically traced to “which Engines, Integrations, deployment options, and price tier fit me” — without a human reconstructing that logic by hand each time.

This taxonomy exists to serve the Configurator Engine (ENG-0004, registered in HVT-0003), the Engine responsible for running this traversal end to end.

Per HVT-0004 §1, this document does not replace prose or the Object Model — it is a governed extension of both, subject to the same rule: if this document and the object graph ever disagree, this document is authoritative until reconciled (HVT-0001 Art. V).

## 2. Two Layers, One Model

Architecture Office decision (2026-08-04): the taxonomy has two layers, not two competing versions.

- Schema layer (abstract): the general classification spine, applicable to every industry the Foundry ever serves.
- Instance layer (applied): one real business’s path through that spine — a specific example, not a type definition.

### 2.1 Schema Layer — The Taxonomy Spine

```
Sector
   ↓
Industry
   ↓
Business Type
   ↓
Business Model
   ↓
Workflow
   ↓
Problem
   ↓
Solution (Engine)
   ↓
Package
   ↓
Product
   ↓
Integration
```

Each level narrows the one above it. A Sector contains many Industries; an Industry contains many Business Types; a Business Type may operate under more than one Business Model (e.g., solo operator vs. multi-chair salon); each Business Model has characteristic Workflows; each Workflow surfaces recurring Problems; each Problem is matched to one or more Solutions (Engines); each Engine is delivered as one or more Packages; each Package is offered as a Product; each Product connects to external systems via Integrations.

### 2.2 Schema-Layer Walk — Hair Salon (Now a Registered Instance)

Per DR-2026-08-04-04, this example is promoted from illustrative documentation to a real registered instance in the object graph. The objects below now exist as first-class graph entries, not prose-only examples.

| Schema Level | Hair Salon Instance | Object ID |
|---|---|---|
| Sector | Services | SEC-0001 |
| Market Industry | Personal Care | MKT-0001 |
| Business Type | Hair Salon | BUT-0001 |
| Business Model | (not yet specified — deferred; see §8) | — |
| Problem | Missed appointments · Empty time slots · No repeat customers · Manual stock · Slow checkout | PRB-0001–PRB-0005 |
| Solution (Engine) | Local Customer Engine (ENG-0001) · Local Content & Booking Engine (ENG-0002) · Commerce Engine (ENG-0003) | ENG-0001–0003 |
| Integration | Stripe · Square · Google Calendar · Apple Calendar · WhatsApp Business · Xero · QuickBooks | INT-0001–INT-0007 |
| Deployment (cross-cutting, §4) | Web · Tablet · Phone · PWA | — (attribute) |
| Pricing (cross-cutting, §4) | Basic · Professional · Enterprise | — (attribute) |

Engine gap, not silently filled: Howard’s original example named two capabilities — Stock management and Review/reply management — for which no Engine is registered. Per HVT-0001 Art. II, these are logged as Engine Search candidates, not built. See §2.3’s required_capabilities field for how the gap is represented on the canonical card itself, so it stays visible rather than disappearing into a clean-looking list.

### 2.3 Canonical Query Shape — the BusinessType Card

Per DR-2026-08-04-04, this layers on top of the schema in §2.1 — it does not replace it. The graph objects in §2.2 remain the traceable, normalized source of truth (HVT-0004 §6: query by traversal, provenance per object). BusinessType is a denormalized read view: one flat record per business type, generated from the underlying graph, so a human or the Configurator Engine (ENG-0004) can answer “what does this business need” in a single lookup instead of a multi-hop traversal.

```yaml
BusinessType:
  id:                      # BUT-####
  name:
  sector:                  # denormalized rollup of classifies_under → Market Industry → Sector
  common_problems:         # list of Problem names (from `solves` edges into this Business Type's Engines)
  required_capabilities:   # list — capabilities with no gap, or explicitly flagged as "Engine Search pending"
  optional_capabilities:   # list — capabilities that enhance but aren't required
  recommended_engines:     # list of Engine IDs (only Engines actually registered in HVT-0003)
  recommended_packages:    # list of Package IDs — empty/pending if no Package built yet from the Engine
  integrations:            # list of Integration IDs
  deployment_targets:      # subset of {Web, Tablet, Phone, PWA}
  pricing_bands:           # subset of {Basic, Professional, Enterprise}
  time_to_deploy:          # estimate, e.g. "same session" / "under 1 day" / "1-2 weeks"
  complexity_score:        # 1-5, Foundry-internal estimate of integration/config effort
```

First real card — Hair Salon (BUT-0001):

```yaml
BusinessType:
  id: BUT-0001
  name: Hair Salon
  sector: Personal Care                # via MKT-0001, under SEC-0001 Services
  common_problems:
    - Missed appointments
    - Empty time slots
    - No repeat customers
    - Manual stock
    - Slow checkout
  required_capabilities:
    - Appointment booking             # covered: ENG-0002
    - Payment processing              # covered: ENG-0003
    - Customer records / loyalty      # covered: ENG-0001
    - Stock / inventory tracking      # GAP prose restored 2026-09-05 per DR-2026-09-04-10a. Resolution status now lives ONLY in HVT-0006-OVL-0001, not here. See overlay.
  optional_capabilities:
    - Review & reply management       # GAP prose restored 2026-09-05 per DR-2026-09-04-10a. Resolution status now lives ONLY in HVT-0006-OVL-0001, not here. See overlay.
    - Staff rota / timesheets         # not yet modeled — future Workflow candidate
  recommended_engines: [ENG-0001, ENG-0002, ENG-0003]
  recommended_packages: []             # none built yet — Engines exist, Packages do not (Art. III.2 not yet reached); a Commerce decrement-on-payment Package is a future candidate (DR-2026-09-04-10)
  integrations: [INT-0001, INT-0002, INT-0003, INT-0004, INT-0005, INT-0006, INT-0007]
  deployment_targets: [Web, Tablet, Phone, PWA]
  pricing_bands: [Basic, Professional, Enterprise]
  time_to_deploy: "same session, per DOC-0001 §Instant Integration Path"
  complexity_score: 2                 # low-moderate: 3 of 5 required capabilities already have a registered Engine
```

complexity_score here is a first-pass Architecture Office estimate (2 of 5), not a validated metric — flagged for a defined scoring method in a future HVT-0006 revision.

Update, 2026-09-05: the resolved status of the Stock and Review capability gaps (Engine Search DR-2026-09-04-10, both PARTIAL MATCH, no new Engine) is recorded in HVT-0006-OVL-0001, an overlay document, not in this section’s prose. This is a deliberate reversal of this document’s own v0.4 in-place edit, made per DR-2026-09-04-10a’s finding that resolving a Search outcome by editing this taxonomy document’s body directly created a second, competing source of truth alongside the overlay. Read the overlay for current status; this document’s required_capabilities / optional_capabilities entries for Stock and Review are intentionally left at their pre-Search wording.

## 3. New Object Types (Proposed Extension to HVT-0004 §2)

The following object types are required by this taxonomy and do not yet exist in HVT-0004’s Twelve Object Types. They are proposed here, under Architecture Office authority, and are flagged for formal adoption into HVT-0004 (version bump to v0.2) rather than silently added to the canonical list — per HVT-0001 Art. V, no document is amended by another document’s side effect.

| Proposed Type | Definition | ID Prefix |
|---|---|---|
| Sector | The broadest market grouping (e.g., Services, Retail, Hospitality). Parent of Market Industry. | SEC-#### |
| Market Industry | A recognized vertical within a Sector (e.g., Personal Care). Parent of Business Type. Named “Market Industry” rather than “Industry” to avoid collision with HVT-0003’s existing “Industry Template” asset class, which retains IND-####. Resolved 2026-08-04, see DR-2026-08-04-04 §2.2. | MKT-#### |
| Business Type | A specific kind of business within an Industry (e.g., Hair Salon). | BUT-#### |
| Business Model | A structural variant of a Business Type (e.g., solo operator vs. multi-location chain) affecting which Workflows and Packages apply. | BUM-#### |
| Problem | A recurring, named pain point surfaced by a Workflow, matched to one or more Solutions. | PRB-#### |
| Integration | An external system or service a Product connects to (e.g., Stripe, Google Calendar). Distinct from Engine — an Integration is consumed, not built by the Foundry. | INT-#### |
| Product | The customer-facing, purchasable configuration of a Package — what the owner actually sees and buys. | PRD-#### |

Types already defined in HVT-0004 and reused without change: Workflow, Engine, Package, Asset, Document, Decision.

## 4. Cross-Cutting Dimensions (Not Taxonomy Levels)

Deployment Options, Pricing, Business Size, Budget, and Technical Ability are not levels of the taxonomy spine. They are filter/attribute dimensions that apply at the Product level, used by the Configurator Engine to narrow results after the spine has identified candidate Solutions. Modeling them as attributes rather than hierarchy levels keeps the spine a strict narrowing chain (per §2.1) and keeps these dimensions independently combinable — a Product’s deployment options don’t determine its price tier, and vice versa.

| Dimension | Values (controlled vocabulary) | Applies To |
|---|---|---|
| Deployment | Web · Tablet · Phone · PWA | Product |
| Pricing Tier | Basic · Professional · Enterprise | Product |
| Business Size | 1 Person · 2–5 Staff · 5–20 Staff · 20+ | Business Type instance |
| Budget | £0–50 · £50–200 · £200–1000 · £1000+ | Business Type instance (monthly) |
| Technical Ability | None · Basic · Intermediate · Advanced | Business Type instance |

## 5. New Relationship Types (Proposed Extension to HVT-0004 §5)

| Relationship | Meaning | Example |
|---|---|---|
| works_with | Two Engines (or Products) are compatible and commonly deployed together, neither requiring the other. | Commerce Engine works_with Booking Engine |
| requires | An Engine cannot function without another Engine present. | Commerce Engine requires Customer Engine |
| optional_with | An Engine can be enhanced by another Engine, which is not required. | Commerce Engine optional_with Crypto Engine |
| classifies_under | A lower taxonomy-spine object sits under a higher one. | Hair Salon classifies_under Personal Care |
| solves | A Solution (Engine) addresses a named Problem. | Commerce Engine solves Slow checkout |
| integrates_via | A Product connects to an external system through an Integration object. | Commerce Product integrates_via Stripe |

Existing HVT-0004 relationship types (depends_on, used_by, compatible_with via works_with/optional_with above, contains, governs, owns) are reused unchanged.

## 6. Data Card Schemas

Three reusable card shapes, formalized so the Configurator Engine (and any UI built on it) can render them consistently.

### 6.1 Integration Card

```yaml
Integration:
  id:                   # INT-####
  name:
  category:             # e.g., Payments, Calendar, Accounting, Messaging
  open_source:          # boolean
  monthly_cost:         # string or null (e.g., "None", "£X/mo")
  countries_supported:  # e.g., "170+"
  features:             # list
  compatible_engines:   # list of Engine IDs (integrates_via target)
  alternatives:         # list of other Integration IDs in the same category
```

### 6.2 Engine Compatibility Card

```yaml
EngineCompatibility:
  engine_id:      # ENG-####
  works_with:     # list of Engine IDs
  requires:       # list of Engine IDs
  optional_with:  # list of Engine IDs
```

### 6.3 Sizing Filter Card

```yaml
SizingFilters:
  business_size:      # one of: "1 Person", "2-5 Staff", "5-20 Staff", "20+"
  budget:             # one of: "£0-50", "£50-200", "£200-1000", "£1000+"
  technical_ability:  # one of: "None", "Basic", "Intermediate", "Advanced"
```

### 6.4 Registered Integration Cards (Hair Salon Instance, §2.3)

Seven Integration objects (INT-0001–INT-0007) registered against the Hair Salon BusinessType card. Provenance matters here: Stripe’s card is Howard-supplied data, reproduced as given. The remaining six are Architecture Office best-effort entries from general market knowledge, not verified against current vendor documentation — flagged unverified and must be confirmed before any of them power a real customer-facing configurator.

```yaml
- id: INT-0001
  name: Stripe
  category: Payments
  open_source: false
  monthly_cost: "None (transaction fees apply)"
  countries_supported: "170+"
  features: [Subscriptions, Invoices, Tax]
  compatible_engines: [ENG-0003]          # Commerce; also fits a future Membership/CRM engine per Howard's original card
  alternatives: [INT-0002, "PayPal", "Adyen"]
  provenance: "Howard-supplied, 2026-08-04"
- id: INT-0002
  name: Square
  category: Payments + Point of Sale
  open_source: false
  monthly_cost: "None (transaction fees apply); paid tiers for advanced POS features"
  countries_supported: "~8 (incl. US, UK, Canada, Australia, Ireland, France, Spain, Japan)"
  features: [In-person POS, Online checkout, Invoices, Loyalty add-on]
  compatible_engines: [ENG-0003]
  alternatives: [INT-0001, "PayPal", "SumUp"]
  provenance: "Architecture Office estimate — unverified, confirm before production use"
- id: INT-0003
  name: Google Calendar
  category: Scheduling
  open_source: false
  monthly_cost: "Free (business tiers via Google Workspace)"
  countries_supported: "Global"
  features: [Appointment sync, Reminders, Shared calendars]
  compatible_engines: [ENG-0002]
  alternatives: [INT-0004]
  provenance: "Architecture Office estimate — unverified, confirm before production use"
- id: INT-0004
  name: Apple Calendar
  category: Scheduling
  open_source: false
  monthly_cost: "Free"
  countries_supported: "Global (iCloud accounts)"
  features: [Appointment sync, Reminders]
  compatible_engines: [ENG-0002]
  alternatives: [INT-0003]
  provenance: "Architecture Office estimate — unverified, confirm before production use"
- id: INT-0005
  name: WhatsApp Business
  category: Messaging
  open_source: false
  monthly_cost: "Free (app); paid tiers via WhatsApp Business Platform for automation at scale"
  countries_supported: "Global"
  features: [Booking confirmations, Reminders, Customer chat]
  compatible_engines: [ENG-0001, ENG-0002]
  alternatives: []
  provenance: "Architecture Office estimate — unverified, confirm before production use"
- id: INT-0006
   name: Xero
   category: Accounting
   open_source: false
   monthly_cost: "Paid subscription (tiered)"
   countries_supported: "Primarily UK, AU, NZ, US, with broader multi-currency support"
   features: [Invoicing, Bank reconciliation, Payroll add-on, Tax reporting]
   compatible_engines: [ENG-0003]
   alternatives: [INT-0007]
   provenance: "Architecture Office estimate — unverified, confirm before production use"
- id: INT-0007
   name: QuickBooks
   category: Accounting
   open_source: false
   monthly_cost: "Paid subscription (tiered)"
   countries_supported: "Primarily US, UK, Canada, Australia"
   features: [Invoicing, Bank reconciliation, Payroll add-on, Tax reporting]
   compatible_engines: [ENG-0003]
   alternatives: [INT-0006]
   provenance: "Architecture Office estimate — unverified, confirm before production use"
```

## 7. Configurator Engine (ENG-0004)

A new Engine is registered in HVT-0003 to run the taxonomy traversal described in this document: given a Business Type (and optionally a Business Model and the Sizing Filters of §4), return the matched Problems, Solutions, Packages, Products, and Integrations, filtered by Deployment and Pricing.

Status: Prototype. One real BusinessType instance now exists to test against (BUT-0001, §2.3), but the Engine itself has not yet been built or run — registration precedes implementation, per HVT-0001 Art. III.4’s Prototype state. Depends on: HVT-0006 (this document), HVT-0004 (Object Model it extends). Composable with: ENG-0001, ENG-0002, ENG-0003 (the Configurator Engine orchestrates across all registered Engines; it does not replace any of them).

## 8. Scope — What v0.1 Deferred and What v0.2 Resolved

v0.1 (2026-08-04, DR-2026-08-04-03) defined the taxonomy schema and Configurator Engine registration only, deliberately deferring all instance data and the prefix collision.

v0.2 (2026-08-04, DR-2026-08-04-04) resolves three of v0.1’s four open items:

1. Resolve the IND-#### prefix collision — Resolved. Renamed to Market Industry, prefix MKT-#### (§2.1, §3). IND-#### remains reserved for Industry Template assets per HVT-0003.
2. Formal HVT-0004 version bump (v0.1 → v0.2) to fold in §3’s new object types and §5’s new relationship types as canonical — still open, unchanged from v0.1. This document’s proposed types are used in practice (§2.2’s real instance) ahead of that formal adoption, which is itself consistent with HVT-0001 Art. III.4 (Prototype precedes formal Reusable Asset status) but should not be mistaken for HVT-0004 already having been amended.
3. Populate first real Industry/Business Type/Integration instances — Resolved. Hair Salon (BUT-0001) registered per §2.2–2.3, with supporting Sector, Market Industry, Problem, and Integration objects.
4. Engine Search (HVT-0001 Art. II) for the unregistered capabilities named in the Hair Salon example — narrowed, resolved via overlay, not in-place edit. Of the original four gaps, two are covered by registered Engines (Booking → ENG-0002, Customer Operations → ENG-0001). The remaining two — Stock management and Review/reply management — went through a formal Engine Search (DR-2026-09-04-10) and neither authorized a new Engine. Current status for both lives in HVT-0006-OVL-0001 (an overlay document), not in this section — see DR-2026-09-04-10a for why an overlay was used instead of editing this document’s body.

New open items introduced by v0.2, logged rather than silently carried:

5. The six non-Stripe Integration cards (§6.4) are Architecture Office best-effort entries, unverified against current vendor documentation. Must be confirmed before any of them power a real customer-facing configurator.
6. complexity_score (§2.3) has no defined scoring methodology yet — the value on BUT-0001 is a first-pass estimate, not a validated metric.
7. Business Model (§2.1) remains unspecified for the Hair Salon instance — Howard’s flat BusinessType schema (§2.3) does not carry a dedicated field for it, so its place in the canonical card vs. the underlying graph needs a decision in a future revision.

## 9. Customer Feedback & Wish Loop (Proposed Extension, per DR-2026-08-04-06 and DR-2026-08-04-07)

Two further object types are proposed, extending §3’s list, ahead of the same pending HVT-0004 formal adoption:

| Proposed Type | Definition | ID Prefix |
|---|---|---|
| Customer Wish | A captured piece of customer feedback or a stated want, tied to a live session, that the current registered Engines and Solution Components may not yet fully satisfy. | WSH-#### |
| Customer Session | A live interaction (e.g., a tablet session in-store) during which one or more Customer Wishes are captured. | SES-#### |

### 9.1 Customer Session Schema

```yaml
CustomerSession:
  id:                              # SES-####
  class: Customer Session
  project_id_or_business_type_id:  # PRJ-#### or BUT-####
  date:
  location:                        # optional
  owner:                           # the Foundry agent or human who ran the session
  status:                          # Open → Closed → Actioned
  notes:                           # free text
  linked_wishes:                   # list of WSH-####
```

Status vocabulary (proposed extension to HVT-0004 §4): Open → Closed → Actioned.

### 9.2 Customer Wish Schema

```yaml
CustomerWish:
  id:                    # WSH-####
  class: Customer Wish
  session_id:            # SES-####
  description:           # customer's own words preferred
  priority:              # customer-stated: Must / Should / Could
  status:                # Logged → Under Review → Engine Search Required → Configured → Accepted → Rejected by Customer → Superseded
  linked_problems:       # optional, list of PRB-####
  linked_capabilities:   # optional
  resolution:            # what the Foundry did, or why it is still open
  customer_asset_flag:   # true/false — does this wish create or change a customer-owned asset (Art. VIII)?
```

Status vocabulary (proposed extension to HVT-0004 §4): Logged → Under Review → Engine Search Required → Configured → Accepted → Rejected by Customer → Superseded.

customer_asset_flag is the field that ties this loop to Article VIII directly: a Wish that would create or change a customer-owned asset (their data, their branding, their content) is flagged so the distinction Article VIII 8.2 requires — customer asset vs. Foundry engine, explicit before work begins — is never lost between “the customer asked for it” and “the Foundry built it.”

The loop these types support, registered as a Workflow-class object (WKF-0001, per HVT-0004 §2’s existing Workflow type — no new type needed for the process itself):

```
Tablet Session
      ↓
Capture Wishes
      ↓
Engine Search (Art. II) or Configurator re-run (ENG-0004)
      ↓
New configuration offered for approval
```

Binding rule (DR-2026-08-04-06, restated precisely per DR-2026-08-04-07): a Customer Wish never authorises new Engine code by itself. It only authorises a re-run of the Configurator or a formal Engine Search. This is the same discipline already applied to the Stock and Review capability gaps flagged in §2.3 — a gap is logged and routed through Article II, never quietly filled.

No instance data created this pass. No real Customer Wish or Customer Session has been captured yet; only the types, their fields, and the workflow are registered, consistent with how Problem, Integration, and Solution Component were each proposed as schema before being populated.

## 10. Authority

Issued under HVT-0001 Art. V (traceability), Art. XIII (asset accumulation), and Art. XIV (Model-First Doctrine — the Business Ontology this document specifies is the mechanism Art. XIV requires), HVT-0002 §3.2 (Architecture Office decision authority), and as a direct extension of HVT-0004 (Object Model). See DR-2026-08-04-03 (v0.1), DR-2026-08-04-04 (v0.2), and DR-2026-08-04-06 (v0.3).


## 11. Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-08, -10, -11)

- **Minted:** SEC-0002 Retail; SEC-0003 Trades; MKT-0002 Food & household import retail, MKT-0003 Neighbourhood grocery, MKT-0004 Specialist goods, MKT-0005 Independent goods retail (all under SEC-0002); MKT-0006 Local health & care rooms (under SEC-0001 — not MKT-0001); MKT-0007 Building & joinery (under SEC-0003); PRB-0006 Reviews sit unanswered; PRB-0007…PRB-0033 from the cards.
- **Overlaps:** PRB-0007 and PRB-0005 shared; PRB-0020 family_of PRB-0019; PRB-0021 family_of PRB-0010; PRB-0024 family_of PRB-0001 + PRB-0002; PRB-0028 family_of PRB-0006.
- **Dual type:** primary + also_business_types; routing for BUT-0005 fixed (0002 food import → 0003 owner trust rule → 0004 craft knowledge → else 0005).
- **§8 item 2** (HVT-0004 bump): done — HVT-0004 v1.0. **§8 item 5:** fact-check applied to SLC records; unverified fields stay labelled. **§8 item 6** complexity_score: method adopted (HVT-0004 §9.7). **§8 item 7** Business Model: field adopted; BUT-0001 = “Appointment + service fee; retail of products secondary”.
- **§7 ENG-0004:** built and run as `foundry_os` (Prototype) — Job D.
- **Overlays:** HVT-0006-OVL-0001 … OVL-0007, all v1.0 Approved; index HVT-0006-Q-0001 v1.0.
- **Version discrepancy** (v0.4 vs v0.5 references): v1.0 supersedes both.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Initial draft. Establishes taxonomy spine, cross-cutting dimensions, proposed new object/relationship types, data card schemas, and registers Configurator Engine (ENG-0004) at Prototype status. Schema only — no instance data populated. Architecture Office decision, per Howard direction. |
| 0.2 | 2026-08-04 | Adds §2.3 BusinessType canonical query-shape schema, layered on top of the v0.1 graph model per confirmed scope. Resolves the IND-#### prefix collision (renamed to Market Industry / MKT-####). Registers first real instance: Hair Salon (BUT-0001) with supporting Sector, Market Industry, Problem, and Integration objects. Flags two remaining Engine gaps (Stock, Review) explicitly on the canonical card rather than silently building or omitting them. References new Constitution Article XIV. Per Howard direction and DR-2026-08-04-04. |
| 0.3 | 2026-08-04 | Adds §9, proposing Customer Wish (WSH-####) and Customer Session (SES-####) object types and registering the Tablet Session → Capture Wishes → Engine Search/Configurator → New Configuration workflow (WKF-0001) as a Workflow-class object. No instance data — schema and workflow registration only. Per DR-2026-08-04-06. |
| 0.4 | 2026-08-04 | §9 expanded with full field-level schemas for Customer Session and Customer Wish, including proposed status vocabularies (extension to HVT-0004 §4) and the customer_asset_flag field tying wishes to Article VIII. Binding rule restated in precise form. Still no instance data. Per DR-2026-08-04-07. |
| 0.5 | 2026-09-05 | Reverted the v0.4→(interim) in-place resolution of BUT-0001’s Stock and Review capability status. Per DR-2026-09-04-10a, resolving a Decision Record’s outcome by editing this document’s body directly created a second source of truth alongside the new overlay pattern (HVT-0006-OVL-0001). §2.3’s required_capabilities / optional_capabilities prose for Stock and Review restored to pre-Search GAP wording; current resolved status lives exclusively in the overlay. This document’s own versioned-edit lifecycle (Draft, version bump, changelog) remains legitimate practice under Appendix A.3 for genuinely new content — this revert is specifically about not duplicating a Decision Record’s findings inside a taxonomy document when a dedicated overlay mechanism now exists for that. |
| 0.6 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026. Approved by the founder. Text unchanged from v0.5. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. SEC/MKT/PRB IDs minted, dual-type rule, Business Model and complexity_score, ENG-0004 built (§11). Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-08. |
