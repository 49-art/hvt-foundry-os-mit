Document ID: HVT-0007  
Title: Marketplace Layer & Solution Catalog  
Version: 1.0  
Previous version: 0.2  
Status: Approved  
Previous status (v0.2): Approved by Founder (Travis Lee Swift), 18 Oct 2026  
Approval record: DR-2026-11-20-09 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001 Art. VI, HVT-0002, HVT-0003, HVT-0004, HVT-0006  

---

# HVT-0007 — Marketplace Layer & Solution Catalog

Document Class: Governance Document — Core Architecture (extension) Effective Date: Pending Approval Review Cycle: Annual, or upon material breach

## 1. Purpose

HVT-0006 modeled the path from a business’s classification down to the Problems it faces and the Engines that solve them. This document picks up where HVT-0006’s spine ends — at the point where a Problem, matched to an Engine, needs to be fulfilled by something the customer actually buys, connects, or already owns — and formalizes that as a marketplace, not a product list.

Per Howard’s founding framing for this layer: the Foundry does not become an app builder that happens to have integrations. It becomes a marketplace of solutions, in which the Foundry’s own Engines are one tier among several, not the only tier.

This document is a governed extension of HVT-0006 (Art. V) and, through it, of HVT-0004. It introduces one new object type (Solution Component), one new cross-cutting classification (the Four Tiers), one new controlled vocabulary (Partner Status), and one new Constitutional clause (Article VI.4, see §7).

## 2. The Four Tiers

The Four Tiers classify where a component’s ownership and origin sit — they are not a taxonomy level (HVT-0006 §2.1’s spine still governs how a business’s problems narrow to solutions) and not a technical distinction. They answer one question: who owns this, and under what terms can the Foundry recommend it?

| Tier | Name | What Lives Here | Foundry Ownership |
|---|---|---|---|
| 1 | Open Source | MIT / Apache / GPL / community projects | None — freely usable, no vendor lock-in |
| 2 | Foundry Assets | Engines, Packages, Themes, Plugins, and the Projects built from them (Commerce Engine, Customer Operations, Booking Engine, CRM Engine, Mystic Veil, Sales Trainer) | Foundry-owned, per HVT-0001 Art. XIII |
| 3 | Partner Products | Stripe, Xero, QuickBooks, Apple, Microsoft, Cloudflare, OpenAI, Anthropic, Square, Shopify, and any future contracted provider | Vendor-owned; Foundry integrates, does not own |
| 4 | Customer Assets | Customer website, data, branding, products, documents, IP | Customer-owned outright, per HVT-0001 Art. VIII |

Tier 4 is unchanged from existing Constitutional doctrine — Article VIII already establishes that the Foundry never owns what belongs to the customer. This document does not alter that; it places it in context alongside the other three tiers so the full ownership picture is visible in one place.

Tiers 1 and 3 are the primary subject of this document: Solution Components (§3) are how both are catalogued under one interchangeable schema. Tier 2 (Foundry Assets — Engines, Packages) continues to use the object types HVT-0004 already defines; a Tier 2 asset is not itself a Solution Component, though it is what Solution Components connect to (see compatible_engines, §3).

## 3. Solution Component — A New Object Type

### 3.1 Definition and Relationship to Existing Objects

Solution Component (prefix SLC-####) is the canonical schema for anything in Tier 1 or Tier 3: an interchangeable, vendor-tracked, licensable thing the Foundry recommends to fulfill a Required Capability. It generalizes and supersedes the narrower Integration type introduced in HVT-0006 v0.2 (INT-####).

Resolution of the “hold off” item: when this document was proposed, the exact relationship between Solution Component and the existing Integration objects was left open for confirmation. Pending that confirmation, Architecture Office has taken the most reversible path available, consistent with Article V (never delete, only supersede): the seven existing INT-#### objects are retained unchanged as the historical record, and seven new SLC-#### objects are created with the fuller Solution Component schema, each linked back with a supersedes edge. Nothing about the original Integration type is deleted or renamed. If, on review, the intended relationship turns out to be “Integration is a permanent subtype of Solution Component” rather than “Solution Component replaces Integration,” no data needs to move — only this section’s wording changes.

### 3.2 Schema

```yaml
SolutionComponent:
  id:                    # SLC-####
  name:
  vendor:
  category:
  licence:               # e.g., "Proprietary", "MIT", "Apache-2.0", "GPL-3.0"
  pricing_model:         # e.g., "Transaction", "Subscription", "Free", "Freemium"
  supported_countries:
  supported_industries:  # list, referencing HVT-0006 Market Industry / Business Type where applicable
  dependencies:          # other Solution Components this one requires
  compatible_engines:    # list of Engine IDs (Tier 2) this component connects to
  deployment_method:     # channel or effort description, e.g., "API", "SDK", "5 minutes to enable"
  support_level:         # e.g., "Community", "Standard", "Priority", "Dedicated"
  partner_status:        # controlled vocabulary, see §4
```

Every field maps to a query the Configurator Engine (ENG-0004, HVT-0006 §7) can now answer: “what components are compatible with the Commerce Engine, licensed permissively, and supported in the customer’s country” is a filter over this schema, not a bespoke lookup.

## 4. Partner Status — Controlled Vocabulary

Proposed extension to HVT-0004 §4 (Status Vocabularies by Class), pending the same formal HVT-0004 version-bump adoption already pending from HVT-0006 (still open, see HVT-0006 §8 item 2 and §8 below).

```
Open Source → Public Integration → Verified → Certified → Strategic Partner → Enterprise Partner
```

A component’s status may move forward along this ladder as the underlying relationship changes — e.g., if a contract is signed with a provider, its partner_status is updated in place: nothing else about the component’s record changes. This is the mechanical form of Article VI’s interchangeability principle: a status change is a field update, not a rebuild.

Terminology note, flagged not silently resolved: the worked Stripe example (§5) uses “Official” as a status. “Official” is not one of the six rungs above. Until confirmed, Architecture Office maps “Official” to Verified as the closest existing rung, and flags this mapping for correction if a different rung was intended.

## 5. Worked Examples — Migrated and New Registrations

### 5.1 Stripe (SLC-0001, supersedes INT-0001)

| Field | Value |
|---|---|
| Vendor | Stripe |
| Category | Payments |
| Licence | Proprietary |
| Pricing Model | Transaction |
| Supported Countries | 46+ (see discrepancy note below) |
| Compatible Engines | ENG-0003 (Commerce) — registered. “Membership,” “Subscriptions,” “Invoices” named in the source example are not yet registered Engines; logged as future Engine Search candidates, not created here. |
| Deployment Method | ~5 minutes to enable |
| Support Level | Standard |
| Partner Status | Verified (mapped from “Official,” see §4) |

Discrepancy flagged, not silently resolved: the country-coverage figure for Stripe was given as “170+” when first supplied (DR-2026-08-04-03 §2.3) and as “46+” in this pass. Both are recorded; SLC-0001 carries 46+ as the more recent figure, and INT-0001 (retained, unedited) still shows 170+. Confirm which is current before either is used in customer-facing material.

### 5.2 Square, Google Calendar, Apple Calendar, WhatsApp Business, Xero, QuickBooks (SLC-0002–SLC-0006, superseding INT-0002–INT-0007)

Migrated into the Solution Component schema with partner_status: Public Integration (no formal partnership agreement exists for any of these six; this is the conservative default, not an upgrade from their prior unverified status). licence: Proprietary for all six — none are open-source offerings. Field-level detail (category, pricing, countries) carried forward unchanged from HVT-0006 §6.4, still marked unverified there and here.

### 5.3 Apple Pay (SLC-0008) — First New Tier 3 Registration

Apple was supplied as a multi-product vendor (Apple Pay, Wallet, Maps, Business Connect, Sign in with Apple, StoreKit, Push Notifications). Rather than register all seven as a batch — which would repeat the “collect everything” pattern this whole layer exists to avoid — Architecture Office registers the one product directly comparable to what the Foundry already recommends (Stripe, Square): Apple Pay.

| Field | Value |
|---|---|
| Vendor | Apple |
| Category | Payments |
| Licence | Proprietary |
| Pricing Model | Transaction (via underlying payment processor; Apple itself does not charge merchants directly for Apple Pay) |
| Supported Countries | 70+ markets (Architecture Office estimate — unverified, confirm before production use) |
| Supported Industries | Retail, Restaurant, Salon, Hotels, Healthcare (as given) |
| Compatible Engines | ENG-0003 (Commerce) |
| Deployment Method | SDK / StoreKit integration — not a standalone flow like Stripe Checkout |
| Support Level | Standard |
| Partner Status | Public Integration (no partnership agreement in place; do not mark Certified until one exists — see §4) |

Remaining five Apple products (Wallet, Maps, Business Connect, Sign in with Apple, StoreKit as a distinct capability from the Apple Pay SDK use, Push Notifications) are logged as identified but not registered — future Solution Catalog candidates, each requiring its own capability match against a Business Type’s Required Capabilities (HVT-0006 §2.3) before being added, per the same discipline applied to Engine Search (Art. II).

## 6. The Resolution Chain

This document’s chain operates downstream of HVT-0006’s taxonomy spine, at the point where a Problem has been matched to an Engine:

```
Business Blueprint
      ↓
Required Capability
      ↓
Foundry Engine (Tier 2)
      ↓
Partner Products (Tier 3) ⇄ Open Source Alternatives (Tier 1)
      ↓
Customer Choice
      ↓
Deployment
```

“Business Blueprint” here is the populated BusinessType canonical card (HVT-0006 §2.3) — the output of HVT-0006’s spine becomes the input to this chain. A Required Capability that has a registered Engine (Tier 2) then looks to Tier 1 and Tier 3 Solution Components to actually fulfill it; where both exist, Customer Choice — not the Foundry — decides between them, per §7.

## 7. Constitutional Amendment — Article VI.4

Per Article XI’s amendment procedure, the following clause is proposed as HVT-0001 Article VI.4, extending Article VI (Modularity, Interchangeability, and Documentation Standards) rather than standing as a new Article — this principle is the same interchangeability doctrine Article VI already applies to modules (6.1) and AI providers (6.2), extended to vendor recommendations generally:

6.4 Foundry recommends solutions, not vendors. Vendor recommendations shall be derived from the customer’s requirements, deployment constraints, geography, budget, and existing technology estate, ensuring that interchangeable alternatives remain available wherever practical.

This is Architecture Office’s placement decision, made without a specific confirmation question asked on this point; it is fully reversible — moving this clause into its own Article, if that turns out to be the intended structure, requires only a further amendment, not a rebuild of anything registered under it. See DR-2026-08-04-05.

## 8. Naming

Per Howard’s direction, this catalog is not referred to as a product database. It is the Foundry Solution Catalog — the set of all registered Solution Component records (§3), queryable by capability, industry, licence, pricing model, geography, and partner status.

## 9. Explicitly Deferred — Not Modeled This Pass

- Referral income. Howard’s note that partner recommendations “could eventually earn referral income if agreements are in place”
- is a commercial/business-model concept, not an architectural one.
- It is not represented as a Solution Component field. If and when referral terms exist, they belong in a commercial agreement record referenced by, not embedded in, the component’s catalog entry — so that a component’s technical compatibility data is never entangled with its commercial terms. Flagged for a future decision on where that record type lives.
- Final resolution of Solution Component vs. Integration (§3.1)
- — held open per the person’s explicit “hold off,” pending their direct confirmation.
- HVT-0004 formal adoption of Solution Component, the Four Tiers, and Partner Status as canonical — still pending, same open item carried from HVT-0006 §8.

## 10. Authority

Issued under HVT-0001 Art. V, Art. VI (as amended, §7), Art. XIII, Art. XIV (Model-First Doctrine — this catalog is what Article XIV’s “which combination of reusable Foundry assets” resolves against), HVT-0002 §3.2, and as a governed extension of HVT-0006. See DR-2026-08-04-05.


## 11. Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-09)

- **§3.1 / §9 Integration vs Solution Component — decided:** Solution Component replaces Integration. INT-0001…0007 kept unedited, status Superseded. No new INT- IDs.
- **§4 “Official” — decided:** retired; SLC-0001 Stripe partner_status = **Public Integration** (no partnership agreement exists). “Verified” is reserved for a real vendor verification.
- **§5.2 numbering:** SLC-0002 Square … SLC-0007 QuickBooks confirmed (the “SLC-0002–SLC-0006” range is a typo for 0002–0007).
- **Fact-check applied (DR-2026-09-25-04):** Stripe 46 countries; Apple Pay 101 countries and regions; Xero UK payroll included from Grow. Unchecked fields stay “unverified”.
- **§9 Referral income — decided:** CommercialAgreement (CAG-) record (HVT-0004 v1.0 §9.5); never a catalog field; never quoted in the room.
- **Candidates, not registered:** five further Apple products, Pronto, and the Tier-3 names on BUT cards — shown on the shelf as “unverified candidate” (Art. VI.4).

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-08-04 | Initial draft. Establishes the Four Tiers, Solution Component schema, Partner Status ladder, migrates the 7 existing Integration objects to Solution Component shape (superseding, not deleting), registers Apple Pay as first new Tier 3 Partner Product, proposes Constitution Article VI.4. Per Howard direction and DR-2026-08-04-05. |
| 0.2 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026. Approved by the founder. Text unchanged from v0.1. The 'Integration vs Solution Component' point Travis asked to hold stays open (§9). Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Held catalog decisions made (§11). Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-09. |
